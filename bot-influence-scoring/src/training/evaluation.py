import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
import numpy as np

def prepare_masks(data, train_ratio=0.70, val_ratio=0.15):
    """
    Creates stratified train, validation, and test masks for the graph nodes.
    """
    num_nodes = data['user'].x.shape[0]
    labels = data['user'].y.cpu().numpy()
    indices = np.arange(num_nodes)
    
    # Split indices
    train_idx, temp_idx = train_test_split(
        indices, train_size=train_ratio, stratify=labels, random_state=42
    )
    
    # Relative ratio for val and test
    relative_val_ratio = val_ratio / (1 - train_ratio)
    val_idx, test_idx = train_test_split(
        temp_idx, train_size=relative_val_ratio, stratify=labels[temp_idx], random_state=42
    )
    
    # Create boolean masks
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)
    
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True
    
    data['user'].train_mask = train_mask
    data['user'].val_mask = val_mask
    data['user'].test_mask = test_mask
    
    return data

def evaluate(model, data, mask_name='test_mask', device='cpu'):
    model.eval()
    mask = getattr(data['user'], mask_name)
    
    with torch.no_grad():
        logits = model(data.x_dict, data.edge_index_dict)
        preds = logits.argmax(dim=1)
        probs = torch.softmax(logits, dim=1)[:, 1]
        
        y_true = data['user'].y[mask].cpu().numpy()
        y_pred = preds[mask].cpu().numpy()
        y_prob = probs[mask].cpu().numpy()
        
        metrics = {
            'f1': f1_score(y_true, y_pred, average='macro'),
            'accuracy': accuracy_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_prob)
        }
    
    return metrics
