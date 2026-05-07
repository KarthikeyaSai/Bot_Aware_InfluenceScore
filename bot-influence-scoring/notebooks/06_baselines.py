import torch
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import os

def run_baselines(graph_path):
    data = torch.load(graph_path, weights_only=False)
    X = data['user'].x.numpy()
    y = data['user'].y.numpy()
    
    # Regenerate masks (stratified split)
    indices = np.arange(len(y))
    train_idx, temp_idx = train_test_split(indices, train_size=0.7, stratify=y, random_state=42)
    val_idx, test_idx = train_test_split(temp_idx, train_size=0.5, stratify=y[temp_idx], random_state=42)
    
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    
    print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")
    
    # 1. Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    
    print("\n=== Random Forest Results ===")
    print(f"F1 (Macro): {f1_score(y_test, rf_preds, average='macro'):.4f}")
    print(f"Accuracy:   {accuracy_score(y_test, rf_preds):.4f}")
    print(classification_report(y_test, rf_preds))
    
    # 2. XGBoost
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb.fit(X_train, y_train)
    xgb_preds = xgb.predict(X_test)
    
    print("\n=== XGBoost Results ===")
    print(f"F1 (Macro): {f1_score(y_test, xgb_preds, average='macro'):.4f}")
    print(f"Accuracy:   {accuracy_score(y_test, xgb_preds):.4f}")
    print(classification_report(y_test, xgb_preds))

if __name__ == "__main__":
    run_baselines("data/cresci-2017/processed/hetero_graph.pt")
