import torch
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.gat import BotAwareGAT
from src.training.evaluation import prepare_masks, evaluate
from src.training.trainer import train_model

# Set paths
GRAPH_PATH = "data/cresci-2017/processed/hetero_graph.pt"
MODEL_PATH = "models/gat_cresci2017.pt"
PROBS_PATH = "data/cresci-2017/processed/bot_probabilities.pt"

def main():
    # 1. Device detection
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 2. Load data
    if not os.path.exists(GRAPH_PATH):
        print(f"Error: Graph file not found at {GRAPH_PATH}. Please run Phase 2 first.")
        return
        
    data = torch.load(GRAPH_PATH, weights_only=False)
    
    # 3. Prepare stratified masks
    data = prepare_masks(data)
    
    # 4. Initialize model
    in_channels = data['user'].x.shape[1]
    model = BotAwareGAT(
        in_channels=in_channels,
        hidden_channels=256,
        out_channels=128,
        num_heads=8,
        dropout=0.3,
        edge_types=data.edge_types
    )
    
    print("\nStarting GAT Training...")
    # 5. Train model
    model = train_model(
        model, 
        data, 
        epochs=500, 
        lr=0.001, 
        device=device,
        model_path=MODEL_PATH
    )
    
    # 6. Final Evaluation
    test_metrics = evaluate(model, data, mask_name='test_mask', device=device)
    print("\n=== Final Test Evaluation ===")
    print(f"Test F1 (Macro): {test_metrics['f1']:.4f}")
    print(f"Test Accuracy:   {test_metrics['accuracy']:.4f}")
    print(f"Test ROC-AUC:    {test_metrics['roc_auc']:.4f}")
    
    # 7. Generate and save bot probabilities for ALL nodes
    print("\nGenerating bot probabilities for the full graph...")
    model.eval()
    with torch.no_grad():
        probs = model.get_bot_probabilities(data.x_dict, data.edge_index_dict)
        torch.save(probs.cpu(), PROBS_PATH)
        print(f"Bot probabilities saved to {PROBS_PATH}")
        print(f"Sample probabilities: {probs[:5].cpu().tolist()}")

if __name__ == "__main__":
    main()
