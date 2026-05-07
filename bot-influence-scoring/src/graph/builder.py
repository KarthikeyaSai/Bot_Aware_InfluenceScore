import torch
import numpy as np
import pandas as pd
from torch_geometric.data import HeteroData
from datetime import datetime
from typing import Dict

def compute_recency_score(last_interaction_date: pd.Timestamp, 
                           reference_date: pd.Timestamp,
                           decay_days: float = 30.0) -> float:
    """
    Exponential decay: recent interactions score closer to 1.0.
    """
    if pd.isna(last_interaction_date):
        return 0.0
    days_ago = (reference_date - last_interaction_date).days
    return float(np.exp(-max(0, days_ago) / decay_days))

def compute_edge_weights(interaction_df: pd.DataFrame, alpha: float = 0.6, decay_days: float = 30.0) -> pd.DataFrame:
    """
    interaction_df columns: source_idx, target_idx, timestamp
    Returns: source_idx, target_idx, weight
    """
    # Group by source and target to get frequency and last interaction date
    edges = interaction_df.groupby(['source_idx', 'target_idx']).agg(
        count=('timestamp', 'count'),
        last_date=('timestamp', 'max')
    ).reset_index()

    # Normalize frequency to [0, 1]
    max_count = edges['count'].max()
    edges['f'] = edges['count'] / max_count if max_count > 0 else 0

    # Compute recency score
    reference_date = edges['last_date'].max()
    edges['r'] = edges['last_date'].apply(
        lambda d: compute_recency_score(d, reference_date, decay_days)
    )

    # Composite weight
    edges['weight'] = (alpha * edges['f'] + (1 - alpha) * edges['r']).astype(np.float32)

    return edges[['source_idx', 'target_idx', 'weight']]

def build_heterogeneous_graph(
    node_features: np.ndarray,
    labels: np.ndarray,
    edge_dataframes: Dict[str, pd.DataFrame]
) -> HeteroData:
    """
    Build PyG HeteroData object.
    
    edge_dataframes should contain:
        'follows': df with [source_idx, target_idx, weight]
        'mentions': df with [source_idx, target_idx, weight]
        'retweets': df with [source_idx, target_idx, weight]
    """
    data = HeteroData()

    # Node features and labels
    data['user'].x = torch.from_numpy(node_features).float()
    data['user'].y = torch.from_numpy(labels).long()

    # Edge types
    edge_types = {
        'follows': ('user', 'follows', 'user'),
        'mentions': ('user', 'mentions', 'user'),
        'retweets': ('user', 'retweets', 'user')
    }

    for key, etype in edge_types.items():
        if key in edge_dataframes and not edge_dataframes[key].empty:
            df = edge_dataframes[key]
            data[etype].edge_index = torch.tensor(
                [df['source_idx'].values, df['target_idx'].values], 
                dtype=torch.long
            )
            data[etype].edge_attr = torch.tensor(
                df['weight'].values, 
                dtype=torch.float
            ).unsqueeze(1)
        else:
            # Initialize empty edges if data is missing to keep GNN layers happy
            data[etype].edge_index = torch.empty((2, 0), dtype=torch.long)
            data[etype].edge_attr = torch.empty((0, 1), dtype=torch.float)

    return data

def print_graph_stats(data: HeteroData):
    num_nodes = data['user'].x.shape[0]
    labels = data['user'].y
    num_bots = (labels == 1).sum().item()
    num_genuine = (labels == 0).sum().item()

    print(f"\n=== Graph Statistics ===")
    print(f"Total nodes: {num_nodes:,}")
    print(f"  Genuine users: {num_genuine:,} ({num_genuine/num_nodes*100:.1f}%)")
    print(f"  Bots: {num_bots:,} ({num_bots/num_nodes*100:.1f}%)")
    
    print(f"\nEdge counts:")
    for edge_type in data.edge_types:
        n_edges = data[edge_type].edge_index.shape[1]
        print(f"  {edge_type}: {n_edges:,} edges")
        if n_edges > 0:
            weights = data[edge_type].edge_attr
            print(f"    mean weight: {weights.mean():.4f} | max weight: {weights.max():.4f}")
    
    print(f"\nNode feature dimension: {data['user'].x.shape[1]}")
