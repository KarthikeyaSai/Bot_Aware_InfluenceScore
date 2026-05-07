import os
import pandas as pd
import numpy as np
import torch
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph.features import build_node_features
from src.graph.builder import compute_edge_weights, build_heterogeneous_graph, print_graph_stats

# Set paths
DATA_DIR = "data/cresci-2017/raw"
PROCESSED_DIR = "data/cresci-2017/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_data():
    subsets = [
        "genuine_accounts.csv",
        "social_spambots_1.csv",
        "social_spambots_2.csv",
        "social_spambots_3.csv",
        "traditional_spambots_1.csv",
        "traditional_spambots_2.csv",
        "traditional_spambots_3.csv",
        "traditional_spambots_4.csv"
    ]
    
    all_users = []
    all_tweets = []
    
    for folder in subsets:
        user_path = os.path.join(DATA_DIR, folder, "users.csv")
        tweet_path = os.path.join(DATA_DIR, folder, "tweets.csv")
        
        # Determine label (0 for genuine, 1 for bots)
        label = 0 if folder == "genuine_accounts.csv" else 1
        
        if os.path.exists(user_path):
            u_df = pd.read_csv(user_path, low_memory=False, encoding='latin1')
            u_df['label'] = label
            all_users.append(u_df)
            print(f"Loaded {len(u_df)} users from {folder}")
            
            if os.path.exists(tweet_path):
                t_df = pd.read_csv(tweet_path, low_memory=False, encoding='latin1')
                # Keep only necessary columns for edge extraction and basic stats
                cols = ['id', 'user_id', 'in_reply_to_user_id', 'retweeted_status_id', 'timestamp', 'text']
                t_df = t_df[[c for c in cols if c in t_df.columns]]
                all_tweets.append(t_df)
                print(f"  Loaded {len(t_df)} tweets")
    
    users_df = pd.concat(all_users, ignore_index=True)
    tweets_df = pd.concat(all_tweets, ignore_index=True) if all_tweets else pd.DataFrame()
    
    return users_df, tweets_df

def main():
    print("Loading data...")
    users_df, tweets_df = load_data()
    
    # Drop duplicates in users (sometimes the same user is in different subsets, though unlikely in Cresci)
    users_df = users_df.drop_duplicates(subset=['id']).reset_index(drop=True)
    
    # Create mapping from user_id to index
    user_id_to_idx = {uid: i for i, uid in enumerate(users_df['id'])}
    
    print(f"Building node features for {len(users_df)} users...")
    X, scaler = build_node_features(users_df, tweets_df)
    labels = users_df['label'].values
    
    print("Extracting edges...")
    edge_dfs = {}
    
    if not tweets_df.empty:
        # 1. Mentions/Replies edges
        # Filter for tweets that are replies to users we have in our users_df
        mentions = tweets_df[
            tweets_df['in_reply_to_user_id'].notna() & 
            (tweets_df['in_reply_to_user_id'] != 0) &
            tweets_df['user_id'].isin(user_id_to_idx) &
            tweets_df['in_reply_to_user_id'].isin(user_id_to_idx)
        ].copy()
        
        if not mentions.empty:
            mentions['source_idx'] = mentions['user_id'].map(user_id_to_idx)
            mentions['target_idx'] = mentions['in_reply_to_user_id'].map(user_id_to_idx)
            mentions['timestamp'] = pd.to_datetime(mentions['timestamp'])
            
            print(f"Found {len(mentions)} raw mention interactions.")
            edge_dfs['mentions'] = compute_edge_weights(mentions)
            print(f"Computed {len(edge_dfs['mentions'])} weighted mention edges.")

    # Followers edges - Cresci-2017 often doesn't provide them in CSV. 
    # If we had them, we'd process them here.
    
    print("Constructing HeteroData graph...")
    data = build_heterogeneous_graph(X, labels, edge_dfs)
    
    print_graph_stats(data)
    
    # Save
    save_path = os.path.join(PROCESSED_DIR, "hetero_graph.pt")
    torch.save(data, save_path)
    print(f"\nGraph saved to {save_path}")

if __name__ == "__main__":
    main()
