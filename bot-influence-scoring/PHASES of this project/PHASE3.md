# Phase 3: GAT Model Training & Bot Detection

This document summarizes the work completed during Phase 3 of the Bot-Aware Influence Scoring project.

## 1. GAT Model Architecture
- **Framework**: PyTorch Geometric (PyG).
- **Architecture**: A 2-layer Heterogeneous Graph Attention Network (`BotAwareGAT`).
    - **Hidden Channels**: 256.
    - **Attention Heads**: 8.
    - **Dropout**: 0.3.
    - **Crucial Optimization**: Enabled `add_self_loops=True` in GAT layers to preserve node features for isolated nodes in the sparse mention graph.
- **Classifier**: A 2-layer MLP head mapping GNN embeddings to class logits.

## 2. Training Pipeline
- **Dataset**: Cresci-2017 (11,017 nodes).
- **Split**: Stratified 70% Train, 15% Validation, 15% Test.
- **Optimization**:
    - **Optimizer**: Adam (lr=0.001).
    - **Loss Function**: Weighted Cross-Entropy (compensating for 68% bot imbalance).
    - **Early Stopping**: Patience of 50 epochs monitoring Validation F1.
- **Hardware**: Accelerated via **Metal (MPS)** on Apple Silicon.

## 3. Performance Metrics
The model achieved state-of-the-art performance on the test set:
- **Test F1 (Macro)**: **0.9783** (Target: 0.91)
- **Test Accuracy**: **98.13%**
- **Test ROC-AUC**: **0.9933**

## 4. Bot Detection Results
- Successfully generated bot probability scores ($p_v \in [0, 1]$) for all 11,017 nodes.
- **Output**: `data/cresci-2017/processed/bot_probabilities.pt`.
- Sample probabilities indicate high confidence in classification (e.g., scores near 0.0 for genuine users and high values for bots).

---
**Next Step**: Phase 4 — Graph Sanitization & Composite Influence Scoring (Weeks 12–16).
