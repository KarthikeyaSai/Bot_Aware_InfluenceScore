import torch
import torch.nn as nn
import os
from src.training.evaluation import evaluate

def get_class_weights(labels):
    """
    Computes class weights to handle imbalance.
    """
    count_0 = (labels == 0).sum().item()
    count_1 = (labels == 1).sum().item()
    total = count_0 + count_1
    
    # Weight = total / (num_classes * count)
    w0 = total / (2 * count_0)
    w1 = total / (2 * count_1)
    
    return torch.tensor([w0, w1], dtype=torch.float)

def train_model(model, data, epochs=200, lr=0.005, weight_decay=5e-4, device='cpu', model_path='models/gat_cresci2017.pt'):
    model = model.to(device)
    data = data.to(device)
    
    weights = get_class_weights(data['user'].y[data['user'].train_mask]).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    best_val_f1 = 0
    patience = 50
    counter = 0
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        logits = model(data.x_dict, data.edge_index_dict)
        loss = criterion(logits[data['user'].train_mask], data['user'].y[data['user'].train_mask])
        
        loss.backward()
        optimizer.step()
        
        # Validation
        val_metrics = evaluate(model, data, mask_name='val_mask', device=device)
        
        if val_metrics['f1'] > best_val_f1:
            best_val_f1 = val_metrics['f1']
            torch.save(model.state_dict(), model_path)
            counter = 0
        else:
            counter += 1
            
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:03d} | Loss: {loss.item():.4f} | Val F1: {val_metrics['f1']:.4f} | Val Acc: {val_metrics['accuracy']:.4f}")
            
        if counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break
            
    # Load best model
    model.load_state_dict(torch.load(model_path, weights_only=True))
    return model
