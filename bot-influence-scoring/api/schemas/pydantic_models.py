from pydantic import BaseModel
from typing import List, Optional

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

# Graph data shapes expected by the frontend
class GraphNodeResponse(BaseModel):
    id: str
    botProb: float
    influenceScore: float

class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    weight: float

class GraphDataResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]

# Comparison shapes
class RankItem(BaseModel):
    nodeId: str
    score: float

class RankDisplacement(BaseModel):
    pctTopKDisplaced: float
    meanDisplacement: float
    kendallsTau: float
    spearmanR: float

class ComparisonResponse(BaseModel):
    rankDisplacement: RankDisplacement
    rawTop20: List[RankItem]
    cleanTop20: List[RankItem]

# Leaderboard row expected by the frontend
class LeaderboardRow(BaseModel):
    rank: int
    nodeId: str
    compositeScore: float
    pagerank: float
    authority: float
    icReach: float
    botProb: float
    rankShift: float

class LeaderboardResponse(BaseModel):
    rows: List[LeaderboardRow]

# Bot-probability detail shape expected by the frontend
class BotProbabilityResponse(BaseModel):
    id: str
    botProb: float
    featureBreakdown: List[dict]
    suspiciousNeighbors: List[dict]
