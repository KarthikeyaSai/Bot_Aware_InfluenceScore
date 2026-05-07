import pandas as pd
import torch
import os

# Global cache for data
DATA_CACHE = {
    'influence_df': None,
    'bot_probs': None,
}

def load_precomputed_data():
    infl_path = "data/cresci-2017/processed/influence_results.csv"
    probs_path = "data/cresci-2017/processed/bot_probabilities.pt"
    
    if os.path.exists(infl_path):
        DATA_CACHE['influence_df'] = pd.read_csv(infl_path)
        print(f"Loaded influence results from {infl_path}")
    
    if os.path.exists(probs_path):
        DATA_CACHE['bot_probs'] = torch.load(probs_path, weights_only=False).numpy()
        print(f"Loaded bot probabilities from {probs_path}")

def get_influence_df():
    return DATA_CACHE['influence_df']

def get_bot_probs():
    return DATA_CACHE['bot_probs']
