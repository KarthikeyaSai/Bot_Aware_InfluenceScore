import numpy as np
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from torch_geometric.data import HeteroData
from typing import Dict

def single_ic_simulation(seed_node: int, 
                          adj_matrix: csr_matrix,
                          edge_probs: Dict[tuple, float]) -> int:
    """
    Single IC simulation from a seed node.
    """
    activated = {seed_node}
    frontier = {seed_node}

    while frontier:
        new_frontier = set()
        for u in frontier:
            # Get neighbors from sparse matrix
            start, end = adj_matrix.indptr[u], adj_matrix.indptr[u+1]
            neighbors = adj_matrix.indices[start:end]
            
            for v in neighbors:
                if v not in activated:
                    # Probability of activation
                    p = edge_probs.get((u, v), 0.1)
                    if np.random.random() < p:
                        activated.add(v)
                        new_frontier.add(v)
        frontier = new_frontier

    return len(activated)

def compute_ic_reach(data: HeteroData,
                     n_simulations: int = 100,
                     n_jobs: int = -1) -> Dict[int, float]:
    """
    Compute expected IC propagation reach for each node.
    """
    num_nodes = data['user'].x.shape[0]
    
    # Build edge probability map and sparse adjacency matrix
    edge_probs = {}
    rows, cols, vals = [], [], []
    
    for edge_type in data.edge_types:
        ei = data[edge_type].edge_index
        ea = data[edge_type].edge_attr
        for i in range(ei.shape[1]):
            u, v = ei[0, i].item(), ei[1, i].item()
            w = ea[i].item() if ea is not None else 0.1
            edge_probs[(u, v)] = max(edge_probs.get((u, v), 0), w)

    for (u, v), w in edge_probs.items():
        rows.append(u); cols.append(v); vals.append(1.0)
    
    adj = csr_matrix((vals, (rows, cols)), shape=(num_nodes, num_nodes))

    def compute_node_reach(node_id):
        # Set seed for reproducibility in parallel
        np.random.seed(node_id)
        results = [
            single_ic_simulation(node_id, adj, edge_probs)
            for _ in range(n_simulations)
        ]
        return node_id, np.mean(results)

    print(f"Starting IC simulations for {num_nodes} nodes...")
    results = Parallel(n_jobs=n_jobs)(
        delayed(compute_node_reach)(i) for i in range(num_nodes)
    )
    
    return dict(results)
