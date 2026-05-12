import numpy as np
from fastapi import APIRouter, HTTPException
from api.db.session import get_influence_df, get_bot_probs, get_edges
from api.schemas.pydantic_models import NodeDetailsResponse, BotProbabilityResponse

router = APIRouter()


@router.get("/{node_idx}", response_model=NodeDetailsResponse)
async def get_node_details(node_idx: int):
    df = get_influence_df()
    probs = get_bot_probs()

    if probs is None:
        raise HTTPException(status_code=503, detail="Bot probabilities not loaded.")

    if node_idx < 0 or node_idx >= len(probs):
        raise HTTPException(status_code=404, detail=f"Node index {node_idx} out of range.")

    prob = float(probs[node_idx])
    is_bot = prob >= 0.5

    influence_score = None
    if df is not None:
        match = df[df['raw_index'] == node_idx]
        if not match.empty:
            influence_score = float(match.iloc[0]['score_clean'])

    return NodeDetailsResponse(
        node_idx=node_idx,
        is_bot=is_bot,
        bot_probability=prob,
        influence_score=influence_score,
    )


@router.get("/{node_idx}/bot-probability", response_model=BotProbabilityResponse)
async def get_bot_probability(node_idx: int):
    df = get_influence_df()
    probs = get_bot_probs()
    raw_edges = get_edges()

    if probs is None:
        raise HTTPException(status_code=503, detail="Bot probabilities not loaded.")

    if node_idx < 0 or node_idx >= len(probs):
        raise HTTPException(status_code=404, detail=f"Node index {node_idx} out of range.")

    prob = float(probs[node_idx])

    influence_score = None
    if df is not None:
        match = df[df['raw_index'] == node_idx]
        if not match.empty:
            influence_score = float(match.iloc[0]['score_clean'])

    feature_breakdown = [
        {"feature": "bot_probability", "value": f"{prob:.4f}"},
        {"feature": "is_bot", "value": str(prob >= 0.5)},
        {"feature": "influence_score", "value": f"{influence_score:.4f}" if influence_score is not None else "N/A"},
    ]

    suspicious_neighbors = []
    if raw_edges is not None:
        src_arr, dst_arr, _ = raw_edges
        mask = (src_arr == node_idx) | (dst_arr == node_idx)
        neighbor_ids = np.union1d(dst_arr[mask & (src_arr == node_idx)],
                                  src_arr[mask & (dst_arr == node_idx)])
        for nid in neighbor_ids[:10]:
            nid = int(nid)
            if 0 <= nid < len(probs) and probs[nid] >= 0.5:
                suspicious_neighbors.append({"id": str(nid), "botProb": float(probs[nid])})

    return BotProbabilityResponse(
        id=str(node_idx),
        botProb=prob,
        featureBreakdown=feature_breakdown,
        suspiciousNeighbors=suspicious_neighbors,
    )
