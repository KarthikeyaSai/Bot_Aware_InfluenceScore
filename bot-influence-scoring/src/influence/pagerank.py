import networkx as nx
import numpy as np
from torch_geometric.data import HeteroData
from typing import Dict

def compute_pagerank(data: HeteroData, 
                     damping: float = 0.85,
                     max_iter: int = 100) -> Dict[int, float]:
    """
    Compute PageRank on a HeteroData graph by converting it to a NetworkX DiGraph.
    """
    G = nx.DiGraph()
    num_nodes = data['user'].x.shape[0]
    G.add_nodes_from(range(num_nodes))

    for edge_type in data.edge_types:
        ei = data[edge_type].edge_index
        ea = data[edge_type].edge_attr
        
        for i in range(ei.shape[1]):
            u, v = ei[0, i].item(), ei[1, i].item()
            w = ea[i].item() if ea is not None else 1.0
            
            if G.has_edge(u, v):
                # Update weight (averaging or summing depends on preference, here we sum for total intensity)
                G[u][v]['weight'] += w
            else:
                G.add_edge(u, v, weight=w)

    pr = nx.pagerank(G, alpha=damping, max_iter=max_iter, weight='weight')
    return pr
