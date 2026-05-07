from pydantic import BaseModel
from typing import List, Dict, Optional

class NodeScore(BaseModel):
    raw_index: int
    clean_index: Optional[int] = None
    influence_score: float
    bot_probability: float

class TopInfluencersResponse(BaseModel):
    total_genuine_nodes: int
    top_influencers: List[NodeScore]

class NodeDetailsResponse(BaseModel):
    node_idx: int
    is_bot: bool
    bot_probability: float
    influence_score: Optional[float] = None
