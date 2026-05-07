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
    # Create mapping from screen_name to index
    screen_name_to_idx = {str(sn).lower(): i for i, sn in enumerate(users_df['screen_name'])}
    
    print(f"Building node features for {len(users_df)} users...")
    X, scaler = build_node_features(users_df, tweets_df)
    labels = users_df['label'].values
    
    print("Extracting edges...")
    edge_dfs = {}
    
    if not tweets_df.empty:
        # 1. Mentions/Replies edges from explicit columns
        mentions_col = tweets_df[
            tweets_df['in_reply_to_user_id'].notna() & 
            (tweets_df['in_reply_to_user_id'] != 0) &
            tweets_df['user_id'].isin(user_id_to_idx) &
            tweets_df['in_reply_to_user_id'].isin(user_id_to_idx)
        ].copy()
        
        # 2. Extract mentions from text
        import re
        mention_pattern = re.compile(r'@(\w+)')
        
        text_mentions = []
        # To avoid extreme slowness, only process rows with @ or RT
        tweets_with_mentions = tweets_df[tweets_df['text'].str.contains('@', na=False)].copy()
        print(f"Parsing {len(tweets_with_mentions)} tweets for text-based mentions...")
        
        for _, row in tweets_with_mentions.iterrows():
            source_id = row['user_id']
            if source_id not in user_id_to_idx:
                continue
            
            text = str(row['text'])
            found_mentions = mention_pattern.findall(text)
            
            for sn in found_mentions:
                sn_lower = sn.lower()
                if sn_lower in screen_name_to_idx:
                    text_mentions.append({
                        'user_id': source_id,
                        'target_user_id': users_df.iloc[screen_name_to_idx[sn_lower]]['id'],
                        'timestamp': row['timestamp'],
                        'is_retweet': text.startswith('RT @')
                    })
        
        text_mentions_df = pd.DataFrame(text_mentions)
        
        all_mentions = []
        if not mentions_col.empty:
            all_mentions.append(mentions_col[['user_id', 'in_reply_to_user_id', 'timestamp']].rename(
                columns={'in_reply_to_user_id': 'target_user_id'}))
        
        if not text_mentions_df.empty:
            # Separate retweets and mentions
            retweets_df = text_mentions_df[text_mentions_df['is_retweet']].copy()
            mentions_only_df = text_mentions_df[~text_mentions_df['is_retweet']].copy()
            
            if not mentions_only_df.empty:
                all_mentions.append(mentions_only_df[['user_id', 'target_user_id', 'timestamp']])
            
            if not retweets_df.empty:
                retweets_df['source_idx'] = retweets_df['user_id'].map(user_id_to_idx)
                retweets_df['target_idx'] = retweets_df['target_user_id'].map(user_id_to_idx)
                retweets_df['timestamp'] = pd.to_datetime(retweets_df['timestamp'], errors='coerce')
                edge_dfs['retweets'] = compute_edge_weights(retweets_df.dropna(subset=['timestamp']))
                print(f"Computed {len(edge_dfs['retweets'])} weighted retweet edges.")

        if all_mentions:
            final_mentions_df = pd.concat(all_mentions)
            final_mentions_df['source_idx'] = final_mentions_df['user_id'].map(user_id_to_idx)
            final_mentions_df['target_idx'] = final_mentions_df['target_user_id'].map(user_id_to_idx)
            final_mentions_df['timestamp'] = pd.to_datetime(final_mentions_df['timestamp'], errors='coerce')
            edge_dfs['mentions'] = compute_edge_weights(final_mentions_df.dropna(subset=['timestamp']))
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
