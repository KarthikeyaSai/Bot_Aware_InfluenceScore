import torch
from torch_geometric.data import HeteroData
from typing import Tuple, Dict

def sanitize_graph(data: HeteroData, 
                   bot_probs: torch.Tensor, 
                   tau: float = 0.5) -> Tuple[HeteroData, Dict]:
    """
    Remove bot nodes and their incident edges from the graph.
    
    Args:
        data:       Original HeteroData graph
        bot_probs:  Bot probability per node, shape [N]
        tau:        Classification threshold (default 0.5)
    
    Returns:
        clean_data: Sanitized HeteroData graph
        stats:      Dictionary of sanitization statistics
    """
    num_nodes = data['user'].x.shape[0]
    bot_mask = bot_probs >= tau
    genuine_mask = ~bot_mask
    
    # Genuine node indices
    genuine_indices = torch.where(genuine_mask)[0]
    num_genuine = genuine_indices.numel()

    # Map old node indices to new (compressed) indices
    new_idx = torch.full((num_nodes,), -1, dtype=torch.long)
    new_idx[genuine_mask] = torch.arange(num_genuine)

    clean_data = HeteroData()
    clean_data['user'].x = data['user'].x[genuine_mask]
    clean_data['user'].y = data['user'].y[genuine_mask]

    for edge_type in data.edge_types:
        src, rel, dst = edge_type
        ei = data[edge_type].edge_index
        ea = data[edge_type].edge_attr

        # Keep only edges where both endpoints are genuine
        keep = genuine_mask[ei[0]] & genuine_mask[ei[1]]
        clean_ei = new_idx[ei[:, keep]]

        clean_data[src, rel, dst].edge_index = clean_ei
        if ea is not None:
            clean_data[src, rel, dst].edge_attr = ea[keep]

    stats = {
        'original_nodes': num_nodes,
        'bots_removed': int(bot_mask.sum().item()),
        'genuine_retained': num_genuine,
        'pct_nodes_removed': float(bot_mask.sum().item() / num_nodes * 100),
        'original_edges': {
            str(et): data[et].edge_index.shape[1] for et in data.edge_types
        },
        'clean_edges': {
            str(et): clean_data[et].edge_index.shape[1]
            for et in clean_data.edge_types
        }
    }
    
    return clean_data, stats
