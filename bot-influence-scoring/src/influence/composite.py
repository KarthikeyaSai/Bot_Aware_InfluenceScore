import numpy as np
from typing import Dict

def compute_composite_scores(
    pagerank_scores: Dict[int, float],
    authority_scores: Dict[int, float],
    ic_reach_scores: Dict[int, float],
    beta1: float = 1/3,
    beta2: float = 1/3,
    beta3: float = 1/3
) -> Dict[int, float]:
    """
    Composite influence score: φ_v = N(β1·PR(v) + β2·a_v + β3·IC(v))
    """
    nodes = sorted(pagerank_scores.keys())
    
    pr = np.array([pagerank_scores.get(n, 0) for n in nodes])
    av = np.array([authority_scores.get(n, 0) for n in nodes])
    ic = np.array([ic_reach_scores.get(n, 0) for n in nodes])

    # Min-max normalize each component to [0, 1]
    def minmax(x):
        r = x.max() - x.min()
        return (x - x.min()) / r if r > 0 else np.zeros_like(x)

    norm_pr = minmax(pr)
    norm_av = minmax(av)
    norm_ic = minmax(ic)

    raw_score = beta1 * norm_pr + beta2 * norm_av + beta3 * norm_ic

    # Final min-max normalization
    phi = minmax(raw_score)
    
    return {node: float(phi[i]) for i, node in enumerate(nodes)}
