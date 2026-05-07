import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, HeteroConv

class BotAwareGAT(nn.Module):
    def __init__(self,
                 in_channels: int,
                 hidden_channels: int = 128,
                 out_channels: int = 64,
                 num_heads: int = 8,
                 dropout: float = 0.6,
                 edge_types: list = None,
                 add_self_loops: bool = True):
        """
        Heterogeneous GAT for bot detection.
        add_self_loops=False is required for large dense graphs (e.g. MGTAB)
        to avoid segfaults from GATConv's self-loop insertion on huge edge tensors.
        """
        super().__init__()
        self.dropout = dropout

        self.conv1 = HeteroConv({
            edge_type: GATConv(
                in_channels=in_channels,
                out_channels=hidden_channels // num_heads,
                heads=num_heads,
                dropout=dropout,
                add_self_loops=add_self_loops,
            )
            for edge_type in edge_types
        }, aggr='mean')

        self.conv2 = HeteroConv({
            edge_type: GATConv(
                in_channels=hidden_channels,
                out_channels=out_channels,
                heads=num_heads,
                dropout=dropout,
                add_self_loops=add_self_loops,
                concat=False,
            )
            for edge_type in edge_types
        }, aggr='mean')

        self.classifier = nn.Sequential(
            nn.Linear(out_channels, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 2)
        )

    def forward(self, x_dict, edge_index_dict):
        # Layer 1
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {k: F.elu(v) for k, v in x_dict.items()}
        x_dict = {k: F.dropout(v, p=self.dropout, training=self.training)
                  for k, v in x_dict.items()}

        # Layer 2
        x_dict = self.conv2(x_dict, edge_index_dict)
        x_dict = {k: F.elu(v) for k, v in x_dict.items()}

        # Classification logits for 'user' nodes
        logits = self.classifier(x_dict['user'])
        return logits

    def get_bot_probabilities(self, x_dict, edge_index_dict) -> torch.Tensor:
        """Returns bot probability p_v ∈ [0, 1] for each node."""
        logits = self.forward(x_dict, edge_index_dict)
        probs = F.softmax(logits, dim=1)
        return probs[:, 1]
