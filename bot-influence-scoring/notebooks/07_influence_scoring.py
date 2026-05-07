import torch
import os
import sys
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.influence.sanitize import sanitize_graph
from src.influence.pagerank import compute_pagerank
from src.influence.hits import compute_hits
from src.influence.ic import compute_ic_reach
from src.influence.composite import compute_composite_scores

# Set paths
GRAPH_PATH = "data/cresci-2017/processed/hetero_graph.pt"
PROBS_PATH = "data/cresci-2017/processed/bot_probabilities.pt"
OUTPUT_DIR = "data/cresci-2017/processed"

def run_influence_pipeline(data, name="raw"):
    print(f"\n--- Computing influence for {name} graph ---")
    
    # 1. PageRank
    print("Computing PageRank...")
    pr = compute_pagerank(data)
    
    # 2. HITS
    print("Computing HITS...")
    hubs, auth = compute_hits(data)
    
    # 3. IC Reach
    print("Computing IC Reach (Monte Carlo)...")
    ic = compute_ic_reach(data, n_simulations=100)
    
    # 4. Composite
    print("Combining scores...")
    composite = compute_composite_scores(pr, auth, ic)
    
    return composite

def analyze_displacement(scores_raw, scores_clean, mapping, top_k=100):
    """
    scores_raw: {raw_node_idx: score}
    scores_clean: {clean_node_idx: score}
    mapping: {raw_node_idx: clean_node_idx} (only for genuine nodes)
    """
    # Only consider nodes that are in both (genuine nodes)
    genuine_raw_indices = list(mapping.keys())
    
    # Sort by score for raw (only genuine nodes)
    raw_ranks = sorted(genuine_raw_indices, key=lambda x: scores_raw[x], reverse=True)
    raw_rank_map = {node_idx: r for r, node_idx in enumerate(raw_ranks, 1)}
    
    # Sort by score for clean
    clean_ranks = sorted(scores_clean.keys(), key=lambda x: scores_clean[x], reverse=True)
    clean_rank_map = {node_idx: r for r, node_idx in enumerate(clean_ranks, 1)}
    
    # Calculate displacement for top-k genuine nodes in raw graph
    top_k_raw = raw_ranks[:top_k]
    displacements = []
    
    for node_idx in top_k_raw:
        clean_idx = mapping[node_idx]
        r_raw = raw_rank_map[node_idx]
        r_clean = clean_rank_map[clean_idx]
        displacements.append(abs(r_raw - r_clean))
        
    print(f"\n=== Rank Displacement Analysis (Top-{top_k} Genuine Nodes) ===")
    print(f"Mean Rank Displacement: {np.mean(displacements):.2f}")
    print(f"Max Rank Displacement:  {np.max(displacements)}")
    
    # Jaccard similarity of top-k sets
    top_k_clean_indices_mapped_back = [list(mapping.keys())[list(mapping.values()).index(idx)] for idx in clean_ranks[:top_k]]
    intersection = len(set(top_k_raw) & set(top_k_clean_indices_mapped_back))
    print(f"Top-{top_k} Overlap: {intersection}/{top_k} ({intersection/top_k*100:.1f}%)")
    print(f"Rank Displacement (Bot-induced shift): {100 - (intersection/top_k*100):.1f}%")

def main():
    if not os.path.exists(GRAPH_PATH) or not os.path.exists(PROBS_PATH):
        print("Missing required input files. Run Phases 2 and 3 first.")
        return

    # Load data
    data = torch.load(GRAPH_PATH, weights_only=False)
    bot_probs = torch.load(PROBS_PATH, weights_only=False)
    
    # 1. Compute scores on RAW graph
    # (Note: We compute for all nodes, but we'll focus on genuine ones for comparison)
    scores_raw = run_influence_pipeline(data, name="raw")
    
    # 2. Sanitize Graph
    print("\nSanitizing graph (tau=0.5)...")
    clean_data, stats = sanitize_graph(data, bot_probs, tau=0.5)
    print(f"Removed {stats['bots_removed']} bots. Retained {stats['genuine_retained']} genuine nodes.")
    
    # 3. Compute scores on CLEAN graph
    scores_clean = run_influence_pipeline(clean_data, name="sanitized")
    
    # 4. Create mapping for comparison
    num_nodes = data['user'].x.shape[0]
    bot_mask = bot_probs >= 0.5
    genuine_mask = ~bot_mask
    genuine_raw_indices = torch.where(genuine_mask)[0].tolist()
    mapping = {raw_idx: i for i, raw_idx in enumerate(genuine_raw_indices)}
    
    # 5. Analysis
    analyze_displacement(scores_raw, scores_clean, mapping, top_k=100)
    
    # Save results
    results = {
        'genuine_user_id': data['user'].y[genuine_mask].tolist(), # Using y as proxy for ID if needed, or just indices
        'raw_index': genuine_raw_indices,
        'clean_index': [mapping[i] for i in genuine_raw_indices],
        'score_clean': [scores_clean[mapping[i]] for i in genuine_raw_indices]
    }
    pd.DataFrame(results).to_csv(os.path.join(OUTPUT_DIR, "influence_results.csv"), index=False)
    print(f"\nFinal influence scores saved to {OUTPUT_DIR}/influence_results.csv")

if __name__ == "__main__":
    main()
