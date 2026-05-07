import numpy as np
from fastapi import APIRouter, HTTPException, Query
from api.db.session import get_influence_df, get_bot_probs, get_edges
from api.schemas.pydantic_models import (
    GraphDataResponse, GraphNodeResponse, GraphEdgeResponse,
    LeaderboardRow, LeaderboardResponse,
)

router = APIRouter()


def _filter_edges(raw_edges, node_id_set: set[str]) -> list[GraphEdgeResponse]:
    """Vectorised edge filter — fast enough for MGTAB's 1.7M edges."""
    if raw_edges is None:
        return []
    src_arr, dst_arr, w_arr = raw_edges
    # Convert node_id_set to integer set for numpy comparison
    node_int_set = np.array(sorted(int(x) for x in node_id_set), dtype=np.int64)
    src_mask = np.isin(src_arr, node_int_set)
    dst_mask = np.isin(dst_arr, node_int_set)
    mask = src_mask & dst_mask
    srcs = src_arr[mask]
    dsts = dst_arr[mask]
    ws   = w_arr[mask]
    return [
        GraphEdgeResponse(source=str(int(s)), target=str(int(d)), weight=float(w))
        for s, d, w in zip(srcs, dsts, ws)
    ]


def _bot_ratio(dataset: str) -> float:
    """Return approximate bot ratio for proportional raw-graph splitting."""
    return {"cresci-2017": 0.685, "mgtab": 0.27}.get(dataset, 0.5)


@router.get("/graph", response_model=GraphDataResponse)
async def get_graph_data(
    top_k: int = Query(100, gt=0, le=2000),
    graph_type: str = Query("raw"),
    dataset: str = Query("cresci-2017"),
):
    df    = get_influence_df(dataset)
    probs = get_bot_probs(dataset)
    raw_edges = get_edges(dataset)

    if probs is None:
        raise HTTPException(status_code=503, detail=f"Dataset '{dataset}' not loaded.")

    if graph_type == "sanitized" or df is None:
        if df is None:
            raise HTTPException(status_code=503, detail=f"Influence scores for '{dataset}' not available yet.")
        top_df = df.sort_values(by='score_clean', ascending=False).head(top_k)
        nodes = [
            GraphNodeResponse(
                id=str(int(row['raw_index'])),
                botProb=float(probs[int(row['raw_index'])]),
                influenceScore=float(row['score_clean']),
            )
            for _, row in top_df.iterrows()
        ]
    else:
        bot_ratio = _bot_ratio(dataset)
        genuine_k = max(1, int(top_k * (1 - bot_ratio)))
        bot_k = top_k - genuine_k

        genuine_set = set(df['raw_index'].astype(int).tolist())

        genuine_rows = df.sort_values(by='score_clean', ascending=False).head(genuine_k)
        genuine_nodes = [
            GraphNodeResponse(
                id=str(int(row['raw_index'])),
                botProb=float(probs[int(row['raw_index'])]),
                influenceScore=float(row['score_clean']),
            )
            for _, row in genuine_rows.iterrows()
        ]

        bot_indices = sorted(
            [i for i in range(len(probs)) if i not in genuine_set],
            key=lambda i: probs[i],
            reverse=True,
        )[:bot_k]
        bot_nodes = [
            GraphNodeResponse(id=str(i), botProb=float(probs[i]), influenceScore=0.0)
            for i in bot_indices
        ]
        nodes = genuine_nodes + bot_nodes

    node_ids = {n.id for n in nodes}
    edges = _filter_edges(raw_edges, node_ids)
    return GraphDataResponse(nodes=nodes, edges=edges)


# Keep /cresci-2017 path for backwards compatibility with existing frontend hook
@router.get("/cresci-2017", response_model=GraphDataResponse)
async def get_graph_data_cresci(
    top_k: int = Query(100, gt=0, le=2000),
    graph_type: str = Query("raw"),
    dataset: str = Query("cresci-2017"),
):
    return await get_graph_data(top_k=top_k, graph_type=graph_type, dataset=dataset)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    top_k: int = Query(500, gt=0, le=5000),
    graph_type: str = Query("raw"),
    dataset: str = Query("cresci-2017"),
):
    df    = get_influence_df(dataset)
    probs = get_bot_probs(dataset)

    if probs is None:
        raise HTTPException(status_code=503, detail=f"Dataset '{dataset}' not loaded.")
    if df is None:
        raise HTTPException(status_code=503, detail=f"Influence scores for '{dataset}' not available yet.")

    genuine_set = set(df['raw_index'].astype(int).tolist())

    if graph_type == "sanitized":
        sorted_df = df.sort_values(by='score_clean', ascending=False).head(top_k).reset_index(drop=True)
        entries = [
            (int(row['raw_index']), float(row['score_clean']), float(probs[int(row['raw_index'])]))
            for _, row in sorted_df.iterrows()
        ]
    else:
        genuine_entries = [
            (int(row['raw_index']), float(row['score_clean']), float(probs[int(row['raw_index'])]))
            for _, row in df.sort_values(by='score_clean', ascending=False).iterrows()
        ]
        bot_entries = sorted(
            [(i, 0.0, float(probs[i])) for i in range(len(probs)) if i not in genuine_set and probs[i] >= 0.5],
            key=lambda x: x[2], reverse=True,
        )
        all_entries = genuine_entries + bot_entries
        all_entries.sort(key=lambda x: x[1] if x[0] in genuine_set else x[2], reverse=True)
        entries = all_entries[:top_k]

    rows = [
        LeaderboardRow(
            rank=i + 1, nodeId=str(raw_idx),
            compositeScore=score, pagerank=score, authority=score,
            icReach=round(score * 1000, 1), botProb=bot_prob, rankShift=0.0,
        )
        for i, (raw_idx, score, bot_prob) in enumerate(entries)
    ]
    return LeaderboardResponse(rows=rows)
