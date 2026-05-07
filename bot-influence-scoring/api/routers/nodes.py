from fastapi import APIRouter, HTTPException
from api.db.session import get_influence_df, get_bot_probs
from api.schemas.pydantic_models import NodeDetailsResponse

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
        # Check if node is in the sanitized results (meaning it was human)
        match = df[df['raw_index'] == node_idx]
        if not match.empty:
            influence_score = float(match.iloc[0]['score_clean'])
            
    return NodeDetailsResponse(
        node_idx=node_idx,
        is_bot=is_bot,
        bot_probability=prob,
        influence_score=influence_score
    )
