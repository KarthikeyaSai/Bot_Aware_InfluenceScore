import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple

def build_node_features(users_df: pd.DataFrame, tweets_df: pd.DataFrame = None) -> Tuple[np.ndarray, StandardScaler]:
    """
    Build node feature matrix X ∈ R^(|V| x d)
    """
    features = pd.DataFrame(index=users_df.index)

    # 1. Metadata features
    # Convert created_at to datetime
    users_df['created_at'] = pd.to_datetime(users_df['created_at'], errors='coerce')
    
    # Use the latest creation date in the dataset as reference for age calculation
    reference_date = users_df['created_at'].max()
    features['account_age_days'] = (reference_date - users_df['created_at']).dt.days.fillna(0)

    # Log-normalize count features to handle heavy tails
    features['followers_log'] = np.log1p(users_df['followers_count'].fillna(0))
    features['friends_log'] = np.log1p(users_df['friends_count'].fillna(0))
    features['listed_log'] = np.log1p(users_df['listed_count'].fillna(0))
    features['favourites_log'] = np.log1p(users_df['favourites_count'].fillna(0))

    # Ratios
    features['follower_following_ratio'] = (
        users_df['followers_count'].fillna(0) / (users_df['friends_count'].fillna(0) + 1)
    )

    # Profile completeness (bio, profile pic, location, url)
    features['profile_completeness'] = (
        users_df['description'].notna().astype(int) +
        users_df['profile_image_url'].notna().astype(int) +
        users_df['location'].notna().astype(int) +
        users_df['url'].notna().astype(int)
    )
    
    # Binary flags
    features['default_profile'] = users_df['default_profile'].fillna(0).astype(int)
    features['default_profile_image'] = users_df['default_profile_image'].fillna(0).astype(int)
    features['geo_enabled'] = users_df['geo_enabled'].fillna(0).astype(int)
    features['verified'] = users_df['verified'].fillna(0).astype(int)
    features['protected'] = users_df['protected'].fillna(0).astype(int)

    # Text length features
    features['name_len'] = users_df['name'].str.len().fillna(0)
    features['screen_name_len'] = users_df['screen_name'].str.len().fillna(0)
    features['description_len'] = users_df['description'].str.len().fillna(0)

    # 2. Behavioral features (if tweets_df is provided)
    if tweets_df is not None:
        # Group tweets by user_id
        tweet_stats = tweets_df.groupby('user_id').agg(
            total_tweets=('id', 'count'),
            retweet_count=('retweeted_status_id', lambda x: x.notna().sum()),
            url_count=('text', lambda x: x.str.contains('http', na=False).sum()),
            # Add more behavioral features if needed
        ).reset_index()
        
        # Merge with users
        users_with_stats = users_df.merge(tweet_stats, left_on='id', right_on='user_id', how='left').fillna(0)
        
        features['posting_frequency'] = users_with_stats['total_tweets'] / (features['account_age_days'] + 1)
        features['retweet_ratio'] = users_with_stats['retweet_count'] / (users_with_stats['total_tweets'] + 1)
        features['url_ratio'] = users_with_stats['url_count'] / (users_with_stats['total_tweets'] + 1)
    else:
        # Fallback or placeholder for behavioral features if only user metadata is available
        # In Cresci-2017, some of these might be in the users.csv already in some versions
        # Let's check for common columns
        if 'statuses_count' in users_df.columns:
            features['posting_frequency'] = users_df['statuses_count'].fillna(0) / (features['account_age_days'] + 1)
        else:
            features['posting_frequency'] = 0
            
        features['retweet_ratio'] = 0
        features['url_ratio'] = 0

    # Handle missing values and infinite results from division
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.fillna(features.median())

    # Standardize
    scaler = StandardScaler()
    X = scaler.fit_transform(features.values)

    return X.astype(np.float32), scaler
