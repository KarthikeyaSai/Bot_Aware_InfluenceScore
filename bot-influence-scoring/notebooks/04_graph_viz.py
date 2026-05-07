import torch
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def visualize_graph(graph_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    data = torch.load(graph_path, weights_only=False)
    
    # 1. Edge Weight Distribution
    plt.figure(figsize=(10, 6))
    for edge_type in data.edge_types:
        weights = data[edge_type].edge_attr
        if weights.numel() > 0:
            sns.histplot(weights.numpy().flatten(), bins=50, label=str(edge_type[1]), kde=True)
    
    plt.title("Edge Weight Distribution")
    plt.xlabel("Weight")
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "edge_weight_distribution.png"))
    
    # 2. Degree Distribution
    # Since it's a small graph, we can compute degrees easily
    plt.figure(figsize=(12, 6))
    
    # We'll focus on the 'mentions' edge type as it's the main one we have
    if ('user', 'mentions', 'user') in data.edge_types:
        edge_index = data['user', 'mentions', 'user'].edge_index
        num_nodes = data['user'].x.shape[0]
        
        # Out-degree
        out_degree = torch.zeros(num_nodes)
        out_degree.scatter_add_(0, edge_index[0], torch.ones(edge_index.shape[1]))
        
        # In-degree
        in_degree = torch.zeros(num_nodes)
        in_degree.scatter_add_(0, edge_index[1], torch.ones(edge_index.shape[1]))
        
        plt.subplot(1, 2, 1)
        sns.histplot(out_degree.numpy(), bins=30, kde=False)
        plt.title("Out-degree Distribution (Mentions)")
        plt.yscale('log')
        plt.xlabel("Degree")
        
        plt.subplot(1, 2, 2)
        sns.histplot(in_degree.numpy(), bins=30, kde=False)
        plt.title("In-degree Distribution (Mentions)")
        plt.yscale('log')
        plt.xlabel("Degree")
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "degree_distribution.png"))
    
    # 3. Label Distribution vs Centrality (In-degree)
    if ('user', 'mentions', 'user') in data.edge_types:
        labels = data['user'].y.numpy()
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=labels, y=in_degree.numpy())
        plt.title("In-degree Centrality: Bots vs Genuine")
        plt.xticks([0, 1], ['Genuine', 'Bot'])
        plt.ylabel("In-degree")
        plt.yscale('symlog')
        plt.savefig(os.path.join(output_dir, "centrality_comparison.png"))

    print(f"Visualizations saved to {output_dir}")

if __name__ == "__main__":
    visualize_graph("data/cresci-2017/processed/hetero_graph.pt", "notebooks")
