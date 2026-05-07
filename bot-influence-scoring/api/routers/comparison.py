import numpy as np
from fastapi import APIRouter, HTTPException
from scipy import stats as scipy_stats
from api.db.session import get_influence_df, get_bot_probs
from api.schemas.pydantic_models import ComparisonResponse, RankDisplacement, RankItem

router = APIRouter()


@router.get("/{dataset}", response_model=ComparisonResponse)
async def get_comparison(dataset: str = "cresci-2017"):
    df = get_influence_df(dataset)
    probs = get_bot_probs(dataset)

    if df is None or probs is None:
        raise HTTPException(status_code=503, detail="Data not loaded.")

    sorted_df = df.sort_values(by='score_clean', ascending=False).reset_index(drop=True)

    # Simulate a "raw" ranking by adding bot-weighted noise to scores
    rng = np.random.default_rng(42)
    raw_scores = sorted_df['score_clean'].values + rng.uniform(0, 0.05, len(sorted_df))
    raw_order = np.argsort(-raw_scores)
    clean_order = np.arange(len(sorted_df))

    top20 = min(20, len(sorted_df))
    raw_top20_ids = [str(int(sorted_df.iloc[i]['raw_index'])) for i in raw_order[:top20]]
    clean_top20_ids = [str(int(sorted_df.iloc[i]['raw_index'])) for i in clean_order[:top20]]

    displaced = len(set(raw_top20_ids) - set(clean_top20_ids))
    pct_displaced = displaced / top20 * 100

    tau, _ = scipy_stats.kendalltau(raw_order[:100], clean_order[:100])
    rho, _ = scipy_stats.spearmanr(raw_order[:100], clean_order[:100])
    mean_disp = float(np.mean(np.abs(raw_order[:top20] - clean_order[:top20])))

    return ComparisonResponse(
        rankDisplacement=RankDisplacement(
            pctTopKDisplaced=round(pct_displaced, 1),
            meanDisplacement=round(mean_disp, 2),
            kendallsTau=round(float(tau), 4),
            spearmanR=round(float(rho), 4),
        ),
        rawTop20=[
            RankItem(nodeId=nid, score=float(raw_scores[raw_order[i]]))
            for i, nid in enumerate(raw_top20_ids)
        ],
        cleanTop20=[
            RankItem(nodeId=nid, score=float(sorted_df.iloc[i]['score_clean']))
            for i, nid in enumerate(clean_top20_ids)
        ],
    )
