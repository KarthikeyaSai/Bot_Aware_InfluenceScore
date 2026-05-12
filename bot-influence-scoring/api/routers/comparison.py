import numpy as np
from fastapi import APIRouter, HTTPException
from scipy import stats as scipy_stats
from api.db.session import get_influence_df, get_bot_probs, get_raw_pagerank, get_clean_pagerank
from api.schemas.pydantic_models import ComparisonResponse, RankDisplacement, RankItem

router = APIRouter()


@router.get("/{dataset}", response_model=ComparisonResponse)
async def get_comparison(dataset: str = "cresci-2017"):
    df = get_influence_df(dataset)
    probs = get_bot_probs(dataset)
    raw_pr   = get_raw_pagerank(dataset)
    clean_pr = get_clean_pagerank(dataset)

    if df is None or probs is None:
        raise HTTPException(status_code=503, detail="Data not loaded.")

    # Work only over nodes present in BOTH PageRank dicts (intersection = genuine nodes
    # with at least one edge on both the raw and sanitized graphs).
    # Nodes that are connected only to bots will be absent from clean_pr and are excluded
    # so the rank comparison is on a common, well-defined baseline.
    all_genuine = df['raw_index'].astype(int).tolist()

    if raw_pr is not None and clean_pr is not None:
        genuine_indices = [idx for idx in all_genuine if idx in raw_pr and idx in clean_pr]
        raw_scores_for_genuine   = np.array([raw_pr[idx]   for idx in genuine_indices])
        clean_scores_for_genuine = np.array([clean_pr[idx] for idx in genuine_indices])
    else:
        genuine_indices = all_genuine
        raw_scores_for_genuine   = np.array([df.loc[df['raw_index'] == idx, 'score_clean'].iloc[0]
                                             for idx in genuine_indices])
        clean_scores_for_genuine = raw_scores_for_genuine.copy()

    # Sort genuine nodes by each score to get orderings
    raw_order   = np.argsort(-raw_scores_for_genuine)    # genuine-list index → raw rank
    clean_order = np.argsort(-clean_scores_for_genuine)  # genuine-list index → clean rank

    N = len(genuine_indices)

    # rank_in_raw[i]   = rank of genuine-node i in the raw ordering (0 = highest)
    # rank_in_clean[i] = rank of genuine-node i in the clean ordering
    rank_in_raw   = np.empty(N, dtype=int)
    rank_in_clean = np.empty(N, dtype=int)
    rank_in_raw[raw_order]     = np.arange(N)
    rank_in_clean[clean_order] = np.arange(N)

    top20 = min(20, N)
    raw_top20_ids   = [str(genuine_indices[i]) for i in raw_order[:top20]]
    clean_top20_ids = [str(genuine_indices[i]) for i in clean_order[:top20]]

    # % of clean top-20 that are not in raw top-20
    displaced     = len(set(clean_top20_ids) - set(raw_top20_ids))
    pct_displaced = displaced / top20 * 100

    # For the top-20 nodes in the CLEAN ranking, how many positions did they move?
    top20_clean_node_positions = clean_order[:top20]          # their indices in genuine_indices
    mean_disp = float(np.mean(np.abs(
        rank_in_raw[top20_clean_node_positions].astype(float) -
        rank_in_clean[top20_clean_node_positions].astype(float)
    )))

    compare_n = min(100, N)
    tau, _ = scipy_stats.kendalltau(rank_in_raw[:compare_n], rank_in_clean[:compare_n])
    rho, _ = scipy_stats.spearmanr(rank_in_raw[:compare_n], rank_in_clean[:compare_n])

    return ComparisonResponse(
        rankDisplacement=RankDisplacement(
            pctTopKDisplaced=round(pct_displaced, 1),
            meanDisplacement=round(mean_disp, 2),
            kendallsTau=round(float(tau), 4),
            spearmanR=round(float(rho), 4),
        ),
        rawTop20=[
            RankItem(nodeId=raw_top20_ids[i], score=float(raw_scores_for_genuine[raw_order[i]]))
            for i in range(top20)
        ],
        cleanTop20=[
            RankItem(nodeId=clean_top20_ids[i], score=float(clean_scores_for_genuine[clean_order[i]]))
            for i in range(top20)
        ],
    )
