from fastapi import APIRouter, HTTPException, Query
from api.db.session import get_influence_df, get_bot_probs
from api.schemas.pydantic_models import TopInfluencersResponse, NodeScore
from typing import List

router = APIRouter()

@router.get("/scores", response_model=TopInfluencersResponse)
async def get_top_influencers(limit: int = Query(10, gt=0, le=100)):
    df = get_influence_df()
    probs = get_bot_probs()
    
    if df is None or probs is None:
        raise HTTPException(status_code=503, detail="Data not loaded. Ensure Phases 3 and 4 were completed.")
        
    # Sort by influence score
    top_df = df.sort_values(by='score_clean', ascending=False).head(limit)
    
    influencers = []
    for _, row in top_df.iterrows():
        raw_idx = int(row['raw_index'])
        influencers.append(NodeScore(
            raw_index=raw_idx,
            clean_index=int(row['clean_index']),
            influence_score=float(row['score_clean']),
            bot_probability=float(probs[raw_idx])
        ))
        
    return TopInfluencersResponse(
        total_genuine_nodes=len(df),
        top_influencers=influencers
    )
