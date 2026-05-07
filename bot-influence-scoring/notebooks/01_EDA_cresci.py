import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set paths
DATA_DIR = "data/cresci-2017/raw"
OUTPUT_DIR = "data/cresci-2017/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_label():
    subsets = {
        "genuine_accounts.csv": 0,
        "social_spambots_1.csv": 1,
        "social_spambots_2.csv": 1,
        "social_spambots_3.csv": 1,
        "traditional_spambots_1.csv": 1,
        "traditional_spambots_2.csv": 1,
        "traditional_spambots_3.csv": 1,
        "traditional_spambots_4.csv": 1
    }
    
    all_users = []
    for folder, label in subsets.items():
        path = os.path.join(DATA_DIR, folder, "users.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['label'] = label
            df['subset'] = folder
            all_users.append(df)
            print(f"Loaded {len(df)} users from {folder} (label={label})")
        else:
            print(f"Warning: {path} not found.")
            
    return pd.concat(all_users, ignore_index=True)

def run_eda(users):
    print("\n=== EDA SUMMARY ===")
    print(f"Total users: {len(users)}")
    
    # 1. Class distribution
    counts = users['label'].value_counts()
    print("\nClass distribution:")
    print(counts)
    
    plt.figure(figsize=(8, 6))
    sns.countplot(data=users, x='label')
    plt.title("Class Distribution (0: Genuine, 1: Bot)")
    plt.savefig("notebooks/class_distribution.png")
    
    # 2. Missing values
    missing = users.isnull().sum() / len(users) * 100
    print("\nMissing values (top 10):")
    print(missing.sort_values(ascending=False).head(10))
    
    # 3. Account age
    users['created_at'] = pd.to_datetime(users['created_at'], errors='coerce')
    # Filter out invalid dates
    users = users.dropna(subset=['created_at'])
    reference_date = users['created_at'].max()
    users['account_age_days'] = (reference_date - users['created_at']).dt.days
    
    # 4. Feature distributions
    features = ['followers_count', 'friends_count', 'statuses_count', 'favourites_count', 'listed_count', 'account_age_days']
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, col in enumerate(features):
        if col in users.columns:
            # Use log scale or clip for visualization if needed
            sns.histplot(data=users, x=col, hue='label', bins=50, ax=axes[i], element="step", common_norm=False)
            axes[i].set_title(f"Distribution of {col}")
            # Use log scale for heavy-tailed counts
            if col != 'account_age_days' and col != 'profile_completeness':
                axes[i].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig("notebooks/feature_distributions.png")
    
    # 5. Correlation analysis
    plt.figure(figsize=(10, 8))
    numeric_cols = users.select_dtypes(include=[np.number]).columns
    sns.heatmap(users[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.savefig("notebooks/correlation_heatmap.png")
    
    print("\nEDA completed. Plots saved in notebooks/ directory.")
    
    # Save combined users for phase 2
    users.to_csv(os.path.join(OUTPUT_DIR, "users_labeled.csv"), index=False)
    print(f"Labeled users saved to {os.path.join(OUTPUT_DIR, 'users_labeled.csv')}")

if __name__ == "__main__":
    users_df = load_and_label()
    run_eda(users_df)
