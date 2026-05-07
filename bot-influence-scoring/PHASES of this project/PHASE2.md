# Phase 2: Heterogeneous Graph Construction

This document summarizes the work completed during Phase 2 of the Bot-Aware Influence Scoring project.

## 1. Data Processing & Interaction Extraction
- **Interaction Data**: Processed over 6 million tweets across all Cresci-2017 subsets.
- **Mention Extraction**: Identified 30,521 raw interactions where users mentioned or replied to each other.
- **Edge Filtering**: Filtered interactions to include only those where both the source and target users are present in the labeled dataset, resulting in 2,335 unique weighted edges.

## 2. Node Feature Engineering
Implemented a robust feature engineering pipeline in `src/graph/features.py`:
- **Metadata Features**: `account_age_days`, log-normalized counts, `follower_following_ratio`, and `profile_completeness`.
- **Behavioral Features**: Extracted from tweet history (`posting_frequency`, `retweet_ratio`, `url_ratio`).
- **Standardization**: Applied `StandardScaler` to ensure all features are on a comparable scale for GNN training.

## 3. Weighted Graph Construction
Implemented the heterogeneous graph builder in `src/graph/builder.py`:
- **Recency Scoring**: Applied exponential decay to interactions to favor recent activity.
- **Edge Weighting**: Combined frequency and recency scores ($\alpha=0.6$) to produce final edge weights.
- **HeteroData Format**: Successfully built a PyTorch Geometric `HeteroData` object with node features, labels, and multiple edge types.

## 4. Graph Statistics
- **Total Nodes**: 11,017
    - **Genuine Users**: 3,474 (31.5%)
    - **Bots**: 7,543 (68.5%)
- **Edges**:
    - `('user', 'mentions', 'user')`: 2,335 edges (mean weight: 0.1233)
- **Feature Dimension**: 10 features per node.

## 5. Visualizations
Generated the following diagnostic plots:
- `notebooks/edge_weight_distribution.png`: Shows how weights are distributed across interactions.
- `notebooks/degree_distribution.png`: Shows the in-degree and out-degree distributions (log-scale).
- `notebooks/centrality_comparison.png`: Compares the connectivity of bots vs. genuine users.

---
**Next Step**: Phase 3 — GAT Model Training & Bot Detection (Weeks 6–12).
