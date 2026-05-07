import networkx as nx
from torch_geometric.data import HeteroData
from typing import Tuple, Dict

def compute_hits(data: HeteroData, 
                 max_iter: int = 100,
                 tol: float = 1e-8) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Compute Kleinberg's HITS algorithm.
    Returns: (hub_scores, authority_scores)
    """
    G = nx.DiGraph()
    num_nodes = data['user'].x.shape[0]
    G.add_nodes_from(range(num_nodes))

    for edge_type in data.edge_types:
        ei = data[edge_type].edge_index
        for i in range(ei.shape[1]):
            u, v = ei[0, i].item(), ei[1, i].item()
            G.add_edge(u, v)

    hubs, authorities = nx.hits(G, max_iter=max_iter, tol=tol, normalized=True)
    return hubs, authorities
