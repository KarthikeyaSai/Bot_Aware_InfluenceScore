# Phase 4: Graph Sanitization & Composite Influence Scoring

This document summarizes the work completed during Phase 4 of the Bot-Aware Influence Scoring project.

## 1. Graph Sanitization
- **Threshold ($\tau$)**: 0.5 (nodes with bot probability $\ge 0.5$ were removed).
- **Results**:
    - **Original Nodes**: 11,017
    - **Bots Removed**: 7,533
    - **Genuine Nodes Retained**: 3,484
- **Incident Edge Cleanup**: Successfully removed all edges connected to bot nodes, ensuring that the remaining graph consists only of authentic human-to-human interactions.

## 2. Influence Scoring Algorithms
Implemented a multi-metric scoring pipeline in `src/influence/`:
- **PageRank (`pagerank.py`)**: Measures node authority based on weighted incoming mentions and retweets.
- **HITS (`hits.py`)**: Computes Hub and Authority scores using Kleinberg's algorithm.
- **Independent Cascade (`ic.py`)**: Estimates the expected reach of information spread using Monte Carlo simulations (100 runs per node, parallelized).

## 3. Composite Influence Score
- **Formula**: $\phi_v = \text{Norm}(\frac{1}{3}\text{PR}(v) + \frac{1}{3}\text{Auth}(v) + \frac{1}{3}\text{IC}(v))$
- **Normalization**: Applied min-max normalization to individual components and the final composite score to ensure $\phi_v \in [0, 1]$.

## 4. Rank Displacement Analysis
Measured the shift in influence rankings for genuine nodes between the **Raw Graph** (where bots inflate centrality) and the **Sanitized Graph**:
- **Top-100 Overlap**: 71.0% (29 out of the top 100 genuine influencers were displaced when bots were removed).
- **Mean Rank Displacement**: 59.63 positions.
- **Max Rank Displacement**: 925 positions.
- **Insight**: The results confirm that social bots significantly distort traditional influence metrics. Nearly **29% of the top human influencers** change when inauthentic activity is filtered out, highlighting the necessity of bot-aware scoring.

## 5. Deliverables
- **Sanitized Influence Dataset**: `data/cresci-2017/processed/influence_results.csv`
- **Core Pipeline Scripts**: Modular Python files for each scoring algorithm.

---
**Next Step**: Phase 5 — Backend API Development (Weeks 16–20).
