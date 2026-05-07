# Bot-Aware Influence Scoring in Social Networks using GNNs
## Complete Project Roadmap — From Scratch to Full-Stack Application

---

## Project Overview

| Attribute | Detail |
|---|---|
| Total duration | ~24 weeks |
| Number of phases | 6 |
| Core ML models | GAT (bot detection), PageRank, HITS, Independent Cascade |
| Benchmark datasets | Cresci-2017 |
| Target F1 (Cresci-2017) | ≥ 0.91 |
| Expected rank displacement | Up to 47% in top-k nodes after sanitization |

### What this project does

Traditional social media influence metrics (follower counts, engagement rates, centrality measures) assume all users are genuine. This project builds a pipeline that:

1. Constructs a heterogeneous weighted social graph from raw interaction data
2. Trains a Graph Attention Network (GAT) to classify each account as a bot or genuine user
3. Removes detected bot nodes from the graph (graph sanitization)
4. Recomputes influence scores on the clean subgraph using a composite metric combining PageRank, HITS, and Independent Cascade propagation
5. Measures how much influence rankings shift after sanitization
6. Exposes the entire pipeline through a REST API and interactive frontend dashboard

### Applications

- Influencer validation for brand partnerships
- Platform safety auditing
- Network integrity research
- Academic benchmarking of bot detection methods

---

## Full Tech Stack Summary

### Machine Learning & Graph

| Library | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| PyTorch | 2.x | Deep learning framework |
| PyTorch Geometric (PyG) | Latest | GNN layers, HeteroData graph format |
| scikit-learn | Latest | Preprocessing, baselines, evaluation |
| XGBoost | Latest | Feature-engineering baseline classifier |
| NetworkX | 3.x | Graph algorithms (PageRank, HITS) |
| scipy | Latest | Sparse matrix operations |
| numpy | Latest | Numerical computation |
| pandas | Latest | Data manipulation and EDA |
| joblib | Latest | Parallel IC Monte Carlo simulations |
| torchmetrics | Latest | F1, AUC-ROC computation |
| CUDA | 12.x | GPU acceleration for GNN training |

### Experiment Tracking & Data

| Tool | Purpose |
|---|---|
| MLflow or Weights & Biases | Hyperparameter logging, loss curves, model registry |
| DVC (Data Version Control) | Versioning large dataset files |
| Git + GitHub | Source code version control |
| Jupyter | EDA notebooks, prototyping |

### Backend

| Library / Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| uvicorn | ASGI server |
| Celery | Async task queue for long-running jobs |
| Redis | Message broker for Celery; caching |
| PostgreSQL | Relational database for scores, run history |
| SQLAlchemy | ORM |
| pydantic | Request/response validation |
| Docker + docker-compose | Containerization of all services |
| pytest | Backend testing |

### Frontend

| Library / Tool | Purpose |
|---|---|
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool and dev server |
| TanStack Query | Server state management, caching |
| D3.js | Force-directed interactive graph visualization |
| Recharts | Charts (bar, scatter, line) |
| Tailwind CSS | Styling |
| shadcn/ui | Accessible UI component library |
| Zustand | Client-side state management |
| WebSocket | Real-time progress streaming |

---

## Phase 1 — Environment Setup & Data Acquisition
**Duration:** Weeks 1–3  
**Goal:** Zero to a running Python environment with both benchmark datasets loaded and explored.

---

### 1.1 Python Environment Setup

**Step 1 — Install Python 3.10+**

Download from python.org or use a version manager like `pyenv`:
```bash
pyenv install 3.10.12
pyenv global 3.10.12
```

**Step 2 — Create a virtual environment**

Using conda (recommended for scientific computing):
```bash
conda create -n bot-influence python=3.10
conda activate bot-influence
```

Or using venv:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

**Step 3 — Install core scientific packages**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install torch_geometric
pip install pandas numpy scipy scikit-learn matplotlib seaborn jupyter
pip install xgboost torchmetrics tqdm joblib
pip install mlflow  # or: pip install wandb
```

**Step 4 — Verify GPU availability**
```python
import torch
print(torch.cuda.is_available())   # Should print True
print(torch.cuda.get_device_name(0))
```

---

### 1.2 Project Directory Structure

Create the following folder layout from the start:

```
bot-influence-scoring/
│
├── data/
│   ├── cresci-2017/
│   │   ├── raw/              # Original downloaded files
│   │   └── processed/        # Cleaned CSVs, PyG graph files (.pt)
│
├── notebooks/
│   ├── 01_EDA_cresci.ipynb
│   ├── 03_graph_construction.ipynb
│   ├── 04_gat_training.ipynb
│   └── 05_influence_scoring.ipynb
│
├── src/
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── builder.py         # Heterogeneous graph construction
│   │   └── features.py        # Node feature encoding
│   ├── models/
│   │   ├── __init__.py
│   │   ├── gat.py             # GAT architecture
│   │   └── baselines.py       # Random Forest, XGBoost baselines
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   └── evaluation.py
│   ├── influence/
│   │   ├── __init__.py
│   │   ├── sanitize.py        # Bot removal
│   │   ├── pagerank.py
│   │   ├── hits.py
│   │   ├── ic.py              # Independent Cascade simulation
│   │   └── composite.py       # Composite score formula
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
│
├── api/
│   ├── main.py                # FastAPI app entry point
│   ├── routers/
│   │   ├── analyze.py
│   │   ├── scores.py
│   │   └── nodes.py
│   ├── tasks/
│   │   └── celery_tasks.py
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   └── schemas/
│       └── pydantic_models.py
│
├── frontend/
│   └── (React app — created separately with Vite)
│
├── models/                    # Saved model checkpoints
│   └── gat_cresci2017.pt
│
├── tests/
│   ├── test_graph.py
│   ├── test_model.py
│   └── test_api.py
│
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.worker
├── pyproject.toml
├── .dvcignore
├── .gitignore
└── README.md
```

---

### 1.3 Version Control Setup

```bash
git init
git add .
git commit -m "Initial project structure"
gh repo create bot-influence-scoring --public
git remote add origin https://github.com/your-username/bot-influence-scoring.git
git push -u origin main
```

**Set up DVC for large data files:**
```bash
pip install dvc dvc-gdrive  # or dvc-s3 for AWS
dvc init
dvc remote add -d myremote gdrive://your-gdrive-folder-id
echo "data/" >> .gitignore
dvc add data/cresci-2017/raw/
git add data/cresci-2017/raw.dvc .gitignore
git commit -m "Track raw Cresci-2017 data with DVC"
```

---

### 1.4 Dataset Acquisition

#### Cresci-2017

- **Source:** [github.com/mariocresci/botometer](https://github.com/mariocresci/botometer) or the original Social Honeypot dataset
- **Alternative mirror:** Search for "Cresci-2017 social spambots dataset" on Zenodo or IEEE DataPort
- **Contents:**
  - ~14,000 labeled accounts (genuine, social spambots 1/2/3, traditional spambots)
  - Account metadata CSV (user_id, followers_count, friends_count, statuses_count, created_at, etc.)
  - Tweets CSV per account
  - Ground-truth labels (bot vs genuine)
- **Size:** ~500MB uncompressed
- **License:** Academic use

---

### 1.5 Exploratory Data Analysis (EDA)

Write a Jupyter notebook for each dataset covering:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load metadata
users = pd.read_csv("data/cresci-2017/raw/users.csv")

# 1. Class distribution
print(users['label'].value_counts())
users['label'].value_counts().plot(kind='bar')

# 2. Missing values audit
print(users.isnull().sum() / len(users) * 100)

# 3. Feature distributions
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, col in enumerate(['followers_count', 'friends_count', 'statuses_count',
                          'favourites_count', 'listed_count', 'account_age_days']):
    axes[i//3][i%3].hist(users[col].clip(upper=users[col].quantile(0.99)), bins=50)
    axes[i//3][i%3].set_title(col)

# 4. Bot vs genuine feature comparison
for col in ['followers_count', 'friends_count', 'statuses_count']:
    print(users.groupby('label')[col].describe())
```

**Key things to check:**
- Class imbalance ratio (bots vs genuine users)
- Columns with >20% missing values (may need imputation or dropping)
- Outliers in follower/following counts (bots often have extreme ratios)
- Temporal patterns in account creation dates

---

### Phase 1 Deliverables Checklist

- [ ] Python 3.10+ environment with all packages installed
- [ ] GPU verified with torch.cuda.is_available() == True
- [ ] Project repository initialized on GitHub
- [ ] DVC configured for data versioning
- [ ] Cresci-2017 downloaded and verified (checksums match)
- [ ] EDA notebooks completed for Cresci-2017
- [ ] Class distribution, missing value report, and feature distribution plots saved

---

## Phase 2 — Heterogeneous Graph Construction
**Duration:** Weeks 3–6  
**Goal:** Convert raw CSV interaction data into weighted heterogeneous graphs in PyG HeteroData format.

---

### 2.1 Understanding Heterogeneous Graphs

The paper models the social network as G = (V, E, W) where:

- **V** — Set of user account nodes
- **E** — Directed edges of three types: follower, mention, retweet
- **W** — Edge weights encoding frequency and recency

**Why heterogeneous?** Bots behave differently across relationship types. A bot may aggressively retweet but never receive mentions. Treating all edges as the same type loses this signal.

---

### 2.2 Node Feature Engineering

Each node v gets a feature vector xv ∈ ℝ^d combining:

**Metadata features (account-level, static):**

| Feature | Description | Notes |
|---|---|---|
| `account_age_days` | Days since account creation | Newer accounts more likely bots |
| `profile_completeness` | Binary flags for: bio, profile pic, location, URL | 0–4 score |
| `follower_following_ratio` | followers / (following + 1) | Bots often follow many, have few followers |
| `followers_count` | Raw follower count | Log-normalize |
| `friends_count` | Number of accounts following | Log-normalize |
| `listed_count` | Times added to lists by others | Proxy for perceived authority |

**Behavioral features (activity-based, dynamic):**

| Feature | Description | Notes |
|---|---|---|
| `posting_frequency` | Tweets per day averaged over account lifetime | Bots post in high bursts |
| `temporal_burstiness` | Coefficient of variation of inter-post intervals | High CV = bursty = bot signal |
| `content_diversity` | Unique tweet ratio (unique / total tweets) | Bots repeat content |
| `interaction_reciprocity` | % of mentions that are reciprocated | Genuine users respond to each other |
| `retweet_ratio` | Retweets / total posts | Bots often only retweet |
| `url_ratio` | Posts containing URLs / total posts | Spam bots post many URLs |

**Implementation:**

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def build_node_features(users_df: pd.DataFrame) -> np.ndarray:
    """
    Build node feature matrix X ∈ R^(|V| x d)
    """
    features = pd.DataFrame()

    # Metadata features
    features['account_age_days'] = (
        pd.Timestamp.now() - pd.to_datetime(users_df['created_at'])
    ).dt.days

    features['followers_log'] = np.log1p(users_df['followers_count'])
    features['friends_log'] = np.log1p(users_df['friends_count'])
    features['listed_log'] = np.log1p(users_df['listed_count'])

    features['follower_following_ratio'] = (
        users_df['followers_count'] / (users_df['friends_count'] + 1)
    )

    features['profile_completeness'] = (
        users_df['description'].notna().astype(int) +
        users_df['profile_image_url'].notna().astype(int) +
        users_df['location'].notna().astype(int) +
        users_df['url'].notna().astype(int)
    )

    # Behavioral features (computed from tweets dataframe separately)
    features['posting_frequency'] = users_df['statuses_count'] / (
        features['account_age_days'] + 1
    )
    features['retweet_ratio'] = users_df['retweet_count'] / (
        users_df['statuses_count'] + 1
    )
    features['url_ratio'] = users_df['url_count'] / (
        users_df['statuses_count'] + 1
    )

    # Handle missing values
    features = features.fillna(features.median())

    # Standardize
    scaler = StandardScaler()
    X = scaler.fit_transform(features.values)

    return X.astype(np.float32), scaler
```

---

### 2.3 Edge Weight Formula

For each edge (u, v) the weight is:

```
w_uv = α · f_uv + (1 − α) · r_uv
```

Where:
- `f_uv` ∈ [0,1] — normalized interaction frequency between u and v
- `r_uv` ∈ [0,1] — recency score of the most recent interaction
- `α` ∈ [0,1] — balancing hyperparameter (default: 0.6)

**Computing recency score:**

```python
import numpy as np
from datetime import datetime

def compute_recency_score(last_interaction_date: datetime, 
                           reference_date: datetime = None,
                           decay_days: float = 30.0) -> float:
    """
    Exponential decay: recent interactions score closer to 1.0
    interactions older than decay_days * 5 score near 0.0
    """
    if reference_date is None:
        reference_date = datetime.now()
    days_ago = (reference_date - last_interaction_date).days
    return float(np.exp(-days_ago / decay_days))

def compute_edge_weights(interaction_df, alpha=0.6, decay_days=30.0):
    """
    interaction_df columns: source, target, count, last_date
    Returns: source, target, weight
    """
    # Normalize frequency to [0, 1]
    max_count = interaction_df['count'].max()
    interaction_df['f'] = interaction_df['count'] / max_count

    # Compute recency score
    reference_date = interaction_df['last_date'].max()
    interaction_df['r'] = interaction_df['last_date'].apply(
        lambda d: compute_recency_score(d, reference_date, decay_days)
    )

    # Composite weight
    interaction_df['weight'] = (
        alpha * interaction_df['f'] + (1 - alpha) * interaction_df['r']
    )

    return interaction_df[['source', 'target', 'weight']]
```

---

### 2.4 Building the PyG HeteroData Graph

```python
import torch
from torch_geometric.data import HeteroData

def build_heterogeneous_graph(
    users_df, 
    follower_edges, 
    mention_edges, 
    retweet_edges,
    node_features: np.ndarray,
    labels: np.ndarray
) -> HeteroData:
    """
    Build PyG HeteroData object from edge dataframes and node features.
    
    Each edge dataframe must have columns: source_idx, target_idx, weight
    (integer indices into the node list, not user IDs)
    """
    data = HeteroData()

    # Node features and labels
    data['user'].x = torch.tensor(node_features, dtype=torch.float)
    data['user'].y = torch.tensor(labels, dtype=torch.long)

    # Follower edges
    data['user', 'follows', 'user'].edge_index = torch.tensor(
        [follower_edges['source_idx'].values,
         follower_edges['target_idx'].values], dtype=torch.long
    )
    data['user', 'follows', 'user'].edge_attr = torch.tensor(
        follower_edges['weight'].values, dtype=torch.float
    ).unsqueeze(1)

    # Mention edges
    data['user', 'mentions', 'user'].edge_index = torch.tensor(
        [mention_edges['source_idx'].values,
         mention_edges['target_idx'].values], dtype=torch.long
    )
    data['user', 'mentions', 'user'].edge_attr = torch.tensor(
        mention_edges['weight'].values, dtype=torch.float
    ).unsqueeze(1)

    # Retweet edges
    data['user', 'retweets', 'user'].edge_index = torch.tensor(
        [retweet_edges['source_idx'].values,
         retweet_edges['target_idx'].values], dtype=torch.long
    )
    data['user', 'retweets', 'user'].edge_attr = torch.tensor(
        retweet_edges['weight'].values, dtype=torch.float
    ).unsqueeze(1)

    return data
```

**Save the graph:**
```python
torch.save(data, 'data/cresci-2017/processed/hetero_graph.pt')
# Load later:
data = torch.load('data/cresci-2017/processed/hetero_graph.pt')
```

---

### 2.5 Graph Statistics to Log

After building the graph, always compute and log these statistics:

```python
def print_graph_stats(data: HeteroData):
    num_nodes = data['user'].x.shape[0]
    labels = data['user'].y
    num_bots = (labels == 1).sum().item()
    num_genuine = (labels == 0).sum().item()

    print(f"=== Graph Statistics ===")
    print(f"Total nodes: {num_nodes:,}")
    print(f"  Genuine users: {num_genuine:,} ({num_genuine/num_nodes*100:.1f}%)")
    print(f"  Bots: {num_bots:,} ({num_bots/num_nodes*100:.1f}%)")
    print(f"  Class imbalance ratio: 1:{num_genuine/num_bots:.1f}")
    print(f"\nEdge counts:")
    for edge_type in data.edge_types:
        n_edges = data[edge_type].edge_index.shape[1]
        weights = data[edge_type].edge_attr
        print(f"  {edge_type[1]}: {n_edges:,} edges | "
              f"mean weight: {weights.mean():.4f} | "
              f"max weight: {weights.max():.4f}")
    print(f"\nNode feature dimension: {data['user'].x.shape[1]}")
```

---

### Phase 2 Deliverables Checklist

- [ ] Node feature engineering pipeline implemented and tested
- [ ] Edge weight formula (w = α·f + (1-α)·r) implemented and validated
- [ ] Heterogeneous graphs built for Cresci-2017
- [ ] The graph saved as PyG HeteroData .pt file
- [ ] Graph statistics report generated and saved
- [ ] Degree distribution and edge type breakdown plots saved

---

## Phase 3 — GAT Model Training & Bot Detection
**Duration:** Weeks 6–12  
**Goal:** Train a Graph Attention Network to classify nodes as bot vs genuine. Achieve F1 ≥ 0.91 on Cresci-2017.

---

### 3.1 GAT Architecture

The Graph Attention Network computes attention-weighted neighborhood aggregations:

**Attention coefficient for neighbor u → node v:**
```
e_vu = LeakyReLU( a^T [W·x_v || W·x_u] )
```

**Softmax normalization:**
```
α_vu = exp(e_vu) / Σ_{k ∈ N(v)} exp(e_vk)
```

**Updated node embedding:**
```
h_v = σ( Σ_{u ∈ N(v)} α_vu · W·x_u )
```

**Implementation using PyG's HeteroConv:**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, HeteroConv, Linear

class BotAwareGAT(nn.Module):
    def __init__(self, 
                 in_channels: int,
                 hidden_channels: int = 128,
                 out_channels: int = 64,
                 num_heads: int = 8,
                 dropout: float = 0.6,
                 edge_types: list = None):
        """
        Heterogeneous GAT for bot detection.
        
        Args:
            in_channels:     Node feature dimension (d)
            hidden_channels: Hidden layer size (recommended: 128)
            out_channels:    Output embedding size (recommended: 64)
            num_heads:       Attention heads (recommended: 8)
            dropout:         Dropout probability (recommended: 0.6)
            edge_types:      List of (src, rel, dst) tuples from HeteroData
        """
        super().__init__()
        self.dropout = dropout

        # Layer 1: HeteroConv with GATConv per edge type
        self.conv1 = HeteroConv({
            edge_type: GATConv(
                in_channels=in_channels,
                out_channels=hidden_channels // num_heads,
                heads=num_heads,
                dropout=dropout,
                add_self_loops=False
            )
            for edge_type in edge_types
        }, aggr='mean')  # Aggregate across edge types

        # Layer 2
        self.conv2 = HeteroConv({
            edge_type: GATConv(
                in_channels=hidden_channels,
                out_channels=out_channels // num_heads,
                heads=num_heads,
                dropout=dropout,
                add_self_loops=False,
                concat=False   # Average heads in final layer
            )
            for edge_type in edge_types
        }, aggr='mean')

        # Classification head → outputs bot probability
        self.classifier = nn.Sequential(
            nn.Linear(out_channels, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 2)   # 2 classes: genuine (0) and bot (1)
        )

    def forward(self, x_dict, edge_index_dict):
        # Layer 1 with ELU activation
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {k: F.elu(v) for k, v in x_dict.items()}
        x_dict = {k: F.dropout(v, p=self.dropout, training=self.training)
                  for k, v in x_dict.items()}

        # Layer 2
        x_dict = self.conv2(x_dict, edge_index_dict)
        x_dict = {k: F.elu(v) for k, v in x_dict.items()}

        # Classification logits for 'user' nodes
        logits = self.classifier(x_dict['user'])
        return logits

    def get_bot_probabilities(self, x_dict, edge_index_dict) -> torch.Tensor:
        """Returns bot probability p_v ∈ [0, 1] for each node."""
        logits = self.forward(x_dict, edge_index_dict)
        probs = F.softmax(logits, dim=1)
        return probs[:, 1]   # Probability of class 1 (bot)
```

---

### 3.2 Training Setup

```python
import torch
from torch_geometric.data import HeteroData
from torchmetrics import F1Score, AUROC
from sklearn.model_selection import train_test_split

def prepare_splits(data: HeteroData, train_ratio=0.70, val_ratio=0.15):
    """Stratified train/val/test split."""
    n = data['user'].x.shape[0]
    labels = data['user'].y.numpy()
    indices = torch.arange(n)

    train_idx, temp_idx = train_test_split(
        indices, test_size=(1-train_ratio), stratify=labels, random_state=42
    )
    val_idx, test_idx = train_test_split(
        temp_idx, test_size=0.5,
        stratify=labels[temp_idx.numpy()], random_state=42
    )

    data['user'].train_mask = torch.zeros(n, dtype=torch.bool)
    data['user'].val_mask   = torch.zeros(n, dtype=torch.bool)
    data['user'].test_mask  = torch.zeros(n, dtype=torch.bool)
    data['user'].train_mask[train_idx] = True
    data['user'].val_mask[val_idx]     = True
    data['user'].test_mask[test_idx]   = True
    return data


def train(model, data, optimizer, criterion, device):
    model.train()
    optimizer.zero_grad()

    logits = model(
        {k: v.to(device) for k, v in data.x_dict.items()},
        {k: v.to(device) for k, v in data.edge_index_dict.items()}
    )

    mask = data['user'].train_mask
    loss = criterion(logits[mask], data['user'].y[mask].to(device))
    loss.backward()
    optimizer.step()
    return loss.item()


def evaluate(model, data, mask, device):
    model.eval()
    f1 = F1Score(task='binary').to(device)
    auc = AUROC(task='binary').to(device)

    with torch.no_grad():
        logits = model(
            {k: v.to(device) for k, v in data.x_dict.items()},
            {k: v.to(device) for k, v in data.edge_index_dict.items()}
        )
        probs = torch.softmax(logits, dim=1)[:, 1]
        preds = (probs > 0.5).long()
        labels = data['user'].y[mask].to(device)

    return {
        'f1':  f1(preds[mask],  labels).item(),
        'auc': auc(probs[mask], labels).item()
    }
```

**Main training loop:**

```python
import mlflow

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load graph
data = torch.load('data/cresci-2017/processed/hetero_graph.pt')
data = prepare_splits(data)

# Handle class imbalance
n_genuine = (data['user'].y == 0).sum().item()
n_bots    = (data['user'].y == 1).sum().item()
class_weights = torch.tensor([n_bots / n_genuine, 1.0]).to(device)

# Model, optimizer, loss
model = BotAwareGAT(
    in_channels=data['user'].x.shape[1],
    hidden_channels=128,
    out_channels=64,
    num_heads=8,
    dropout=0.6,
    edge_types=data.edge_types
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=5e-4, weight_decay=1e-5)
criterion = torch.nn.CrossEntropyLoss(weight=class_weights)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', patience=10, factor=0.5
)

# Training with MLflow tracking
with mlflow.start_run():
    mlflow.log_params({
        'hidden_channels': 128,
        'num_heads': 8,
        'dropout': 0.6,
        'lr': 5e-4,
        'weight_decay': 1e-5
    })

    best_val_f1 = 0
    patience_counter = 0
    EARLY_STOP_PATIENCE = 30

    for epoch in range(1, 301):
        loss = train(model, data, optimizer, criterion, device)
        val_metrics = evaluate(model, data, data['user'].val_mask, device)

        scheduler.step(val_metrics['f1'])
        mlflow.log_metrics({'train_loss': loss, **{f'val_{k}': v 
                             for k, v in val_metrics.items()}}, step=epoch)

        if val_metrics['f1'] > best_val_f1:
            best_val_f1 = val_metrics['f1']
            torch.save(model.state_dict(), 'models/gat_cresci2017.pt')
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOP_PATIENCE:
                print(f"Early stopping at epoch {epoch}")
                break

        if epoch % 10 == 0:
            print(f"Epoch {epoch:03d} | Loss: {loss:.4f} | "
                  f"Val F1: {val_metrics['f1']:.4f} | "
                  f"Val AUC: {val_metrics['auc']:.4f}")

    # Final test evaluation
    model.load_state_dict(torch.load('models/gat_cresci2017.pt'))
    test_metrics = evaluate(model, data, data['user'].test_mask, device)
    mlflow.log_metrics({f'test_{k}': v for k, v in test_metrics.items()})
    print(f"\nTest F1: {test_metrics['f1']:.4f} | Test AUC: {test_metrics['auc']:.4f}")
```

---

### 3.3 Hyperparameter Tuning

Key hyperparameters to tune with a grid or Bayesian search:

| Hyperparameter | Search Range | Notes |
|---|---|---|
| `hidden_channels` | 64, 128, 256 | Larger = more capacity, slower |
| `num_heads` | 4, 8 | Multi-head attention |
| `dropout` | 0.3, 0.5, 0.6 | 0.6 often best for sparse graphs |
| `lr` | 1e-3, 5e-4, 1e-4 | Use scheduler to reduce on plateau |
| `weight_decay` | 1e-4, 1e-5, 0 | Regularization |
| `alpha` (edge weight) | 0.4, 0.6, 0.8 | Balance frequency vs recency |
| `tau` (bot threshold) | 0.3–0.7 | Tune using val set F1 curve |

---

### 3.4 Feature-Engineering Baselines

Train these to quantify the structural benefit of GAT:

```python
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import f1_score

X = data['user'].x.numpy()
y = data['user'].y.numpy()
train_mask = data['user'].train_mask.numpy()
test_mask  = data['user'].test_mask.numpy()

# Random Forest
rf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
rf.fit(X[train_mask], y[train_mask])
rf_f1 = f1_score(y[test_mask], rf.predict(X[test_mask]))
print(f"Random Forest F1: {rf_f1:.4f}")

# XGBoost
xgb = XGBClassifier(scale_pos_weight=n_genuine/n_bots, random_state=42)
xgb.fit(X[train_mask], y[train_mask])
xgb_f1 = f1_score(y[test_mask], xgb.predict(X[test_mask]))
print(f"XGBoost F1: {xgb_f1:.4f}")
```

---

### 3.5 Ablation Studies

Run 4 ablation variants and compare F1 scores in a table:

| Variant | Description |
|---|---|
| Full model | 2-layer hetero-GAT + all features |
| No attention (GCN) | Replace GATConv with GCNConv — no attention weighting |
| Homogeneous edges | Merge all 3 edge types into one type |
| Metadata features only | Remove behavioral features from X |
| No graph (baseline) | Random Forest/XGBoost on X only |

---

### Phase 3 Deliverables Checklist

- [ ] GAT model implemented in `src/models/gat.py`
- [ ] Training pipeline with early stopping and MLflow logging
- [ ] Best model checkpoint saved: `models/gat_cresci2017.pt`
- [ ] Test F1 ≥ 0.91 on Cresci-2017
- [ ] Baseline comparison table (RF, XGBoost, GCN, GAT)
- [ ] Ablation study results table
- [ ] Bot probability scores pv generated for all nodes in the dataset

---

## Phase 4 — Graph Sanitization & Composite Influence Scoring
**Duration:** Weeks 12–16  
**Goal:** Remove bot nodes from the graph and compute clean, composite influence scores. Measure and report rank displacement.

---

### 4.1 Graph Sanitization

**Definition:**
```
V_bot = {v ∈ V | p_v ≥ τ}
G' = (V', E')
V' = V \ V_bot
E' = {(u,v) ∈ E | u ∈ V', v ∈ V'}
```

```python
import torch
from torch_geometric.data import HeteroData

def sanitize_graph(data: HeteroData, 
                   bot_probs: torch.Tensor, 
                   tau: float = 0.5) -> tuple[HeteroData, dict]:
    """
    Remove bot nodes and their incident edges.
    
    Args:
        data:       Original HeteroData graph
        bot_probs:  Bot probability per node, shape [N]
        tau:        Classification threshold (default 0.5)
    
    Returns:
        clean_data: Sanitized HeteroData graph
        stats:      Dictionary of sanitization statistics
    """
    N = data['user'].x.shape[0]
    bot_mask = bot_probs >= tau
    genuine_mask = ~bot_mask

    # Map old node indices to new (compressed) indices
    new_idx = torch.full((N,), -1, dtype=torch.long)
    new_idx[genuine_mask] = torch.arange(genuine_mask.sum())

    clean_data = HeteroData()
    clean_data['user'].x = data['user'].x[genuine_mask]
    clean_data['user'].y = data['user'].y[genuine_mask]

    for edge_type in data.edge_types:
        src, rel, dst = edge_type
        ei = data[edge_type].edge_index   # shape [2, E]
        ea = data[edge_type].edge_attr

        # Keep only edges where both endpoints are genuine
        keep = genuine_mask[ei[0]] & genuine_mask[ei[1]]
        clean_ei = new_idx[ei[:, keep]]

        clean_data[src, rel, dst].edge_index = clean_ei
        if ea is not None:
            clean_data[src, rel, dst].edge_attr = ea[keep]

    stats = {
        'original_nodes': N,
        'bots_removed': bot_mask.sum().item(),
        'genuine_retained': genuine_mask.sum().item(),
        'pct_nodes_removed': bot_mask.sum().item() / N * 100,
        'original_edges': {
            et[1]: data[et].edge_index.shape[1] for et in data.edge_types
        },
        'clean_edges': {
            et[1]: clean_data[et].edge_index.shape[1]
            for et in clean_data.edge_types
        }
    }
    return clean_data, stats
```

---

### 4.2 PageRank Authority

```python
import networkx as nx
import numpy as np

def compute_pagerank(clean_data: HeteroData, 
                     damping: float = 0.85,
                     max_iter: int = 100) -> dict:
    """
    Compute PageRank on the sanitized graph.
    Combines all edge types into a single directed graph.
    Edge weights are averaged across types for the same (u,v) pair.
    """
    G = nx.DiGraph()
    N = clean_data['user'].x.shape[0]
    G.add_nodes_from(range(N))

    for edge_type in clean_data.edge_types:
        ei = clean_data[edge_type].edge_index
        ea = clean_data[edge_type].edge_attr

        for i in range(ei.shape[1]):
            u, v = ei[0, i].item(), ei[1, i].item()
            w = ea[i].item() if ea is not None else 1.0
            if G.has_edge(u, v):
                # Average weights across edge types
                G[u][v]['weight'] = (G[u][v]['weight'] + w) / 2
            else:
                G.add_edge(u, v, weight=w)

    pr = nx.pagerank(G, alpha=damping, max_iter=max_iter, weight='weight')
    return pr   # Dict {node_id: pagerank_score}
```

---

### 4.3 HITS Hub-Authority Decomposition

```python
def compute_hits(clean_data: HeteroData, 
                 max_iter: int = 100,
                 tol: float = 1e-8) -> tuple[dict, dict]:
    """
    Compute Kleinberg's HITS algorithm.
    Returns: (hub_scores, authority_scores) as dicts
    """
    G = nx.DiGraph()
    N = clean_data['user'].x.shape[0]
    G.add_nodes_from(range(N))

    for edge_type in clean_data.edge_types:
        ei = clean_data[edge_type].edge_index
        for i in range(ei.shape[1]):
            G.add_edge(ei[0, i].item(), ei[1, i].item())

    hubs, authorities = nx.hits(G, max_iter=max_iter, tol=tol, normalized=True)
    return hubs, authorities
```

---

### 4.4 Independent Cascade (IC) Propagation Reach

The IC model estimates how far influence spreads from each node. Due to computational expense, use Monte Carlo simulation with parallelism.

```python
import numpy as np
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix

def single_ic_simulation(seed_node: int, 
                          adj_matrix: csr_matrix,
                          edge_weights: dict) -> int:
    """
    Single IC simulation from a seed node.
    Returns the number of nodes activated in the cascade.
    """
    activated = {seed_node}
    frontier = {seed_node}

    while frontier:
        new_frontier = set()
        for u in frontier:
            neighbors = adj_matrix[u].nonzero()[1]
            for v in neighbors:
                if v not in activated:
                    p = edge_weights.get((u, v), 0.1)
                    if np.random.random() < p:
                        activated.add(v)
                        new_frontier.add(v)
        frontier = new_frontier

    return len(activated)


def compute_ic_reach(clean_data: HeteroData,
                     n_simulations: int = 1000,
                     n_jobs: int = -1) -> dict:
    """
    Compute expected IC propagation reach for each node.
    Uses Monte Carlo with parallel simulations.
    
    Args:
        n_simulations: Number of Monte Carlo runs per seed node
        n_jobs:        Number of parallel workers (-1 = all CPUs)
    
    Returns:
        Dict {node_id: expected_reach}
    """
    N = clean_data['user'].x.shape[0]

    # Build edge weight dict
    edge_weights = {}
    for edge_type in clean_data.edge_types:
        ei = clean_data[edge_type].edge_index
        ea = clean_data[edge_type].edge_attr
        for i in range(ei.shape[1]):
            u, v = ei[0, i].item(), ei[1, i].item()
            w = ea[i].item() if ea is not None else 0.1
            # If same edge appears in multiple types, take max weight
            edge_weights[(u, v)] = max(edge_weights.get((u, v), 0), w)

    # Build sparse adjacency matrix
    rows, cols, vals = [], [], []
    for (u, v), w in edge_weights.items():
        rows.append(u); cols.append(v); vals.append(w)
    adj = csr_matrix((vals, (rows, cols)), shape=(N, N))

    def compute_node_reach(node_id):
        results = [
            single_ic_simulation(node_id, adj, edge_weights)
            for _ in range(n_simulations)
        ]
        return node_id, np.mean(results)

    # Parallel computation across all nodes
    results = Parallel(n_jobs=n_jobs, verbose=1)(
        delayed(compute_node_reach)(i) for i in range(N)
    )
    return dict(results)
```

> **Performance note:** For graphs with >50K nodes, computing IC reach for every node is prohibitively expensive. Use one of these strategies:
> - Compute only for top-K nodes by PageRank (top 500–1000)
> - Reduce `n_simulations` to 100–200 for approximate results
> - Use the CELF (Cost-Effective Lazy Forward) approximation

---

### 4.5 Composite Influence Score

```python
def compute_composite_scores(
    pagerank_scores: dict,
    authority_scores: dict,
    ic_reach_scores: dict,
    beta1: float = 1/3,
    beta2: float = 1/3,
    beta3: float = 1/3
) -> dict:
    """
    Composite influence score: φ_v = N(β1·PR(v) + β2·a_v + β3·IC(v))
    where N(·) is min-max normalization.
    
    Returns: Dict {node_id: score in [0,1]}
    """
    assert abs(beta1 + beta2 + beta3 - 1.0) < 1e-6, "βs must sum to 1"
    
    nodes = sorted(pagerank_scores.keys())
    
    pr  = np.array([pagerank_scores.get(n, 0)   for n in nodes])
    av  = np.array([authority_scores.get(n, 0)  for n in nodes])
    ic  = np.array([ic_reach_scores.get(n, 0)   for n in nodes])

    # Min-max normalize each component to [0, 1]
    def minmax(x):
        r = x.max() - x.min()
        return (x - x.min()) / r if r > 0 else np.zeros_like(x)

    raw_score = beta1 * minmax(pr) + beta2 * minmax(av) + beta3 * minmax(ic)

    # Final min-max normalization of composite
    phi = minmax(raw_score)
    return {node: float(phi[i]) for i, node in enumerate(nodes)}
```

---

### 4.6 Rank Displacement Analysis

```python
from scipy.stats import kendalltau, spearmanr

def compute_rank_displacement(
    scores_raw: dict, 
    scores_clean: dict,
    top_k: int = 100
) -> dict:
    """
    Measure how much influence rankings shift after bot removal.
    """
    common_nodes = set(scores_raw.keys()) & set(scores_clean.keys())

    # Rankings on raw graph (higher score = lower rank number)
    raw_ranks = {n: r for r, n in enumerate(
        sorted(common_nodes, key=lambda x: scores_raw[x], reverse=True), 1
    )}
    clean_ranks = {n: r for r, n in enumerate(
        sorted(common_nodes, key=lambda x: scores_clean[x], reverse=True), 1
    )}

    # Rank displacement for each node
    displacement = {n: abs(raw_ranks[n] - clean_ranks[n]) for n in common_nodes}

    # Top-k analysis
    top_k_raw = set(n for n, r in raw_ranks.items() if r <= top_k)
    top_k_clean = set(n for n, r in clean_ranks.items() if r <= top_k)
    displaced_from_top_k = top_k_raw - top_k_clean
    pct_displaced = len(displaced_from_top_k) / top_k * 100

    # Rank correlation
    ordered = sorted(common_nodes)
    raw_vec   = [raw_ranks[n]   for n in ordered]
    clean_vec = [clean_ranks[n] for n in ordered]

    kt, _ = kendalltau(raw_vec, clean_vec)
    sr, _ = spearmanr(raw_vec, clean_vec)

    return {
        'top_k': top_k,
        'pct_top_k_displaced': pct_displaced,
        'displaced_nodes': len(displaced_from_top_k),
        'mean_displacement': np.mean(list(displacement.values())),
        'max_displacement': max(displacement.values()),
        'kendalls_tau': kt,
        'spearman_r': sr
    }
```

---

### Phase 4 Deliverables Checklist

- [ ] Sanitized graph G' produced for the dataset
- [ ] PageRank, HITS, and IC scores computed on G'
- [ ] Composite φv ∈ [0,1] scores for all retained nodes
- [ ] Rank displacement report (target: ~47% displacement in top-100 nodes)
- [ ] Before/after ranking comparison plots saved
- [ ] Sensitivity analysis of τ threshold (0.3–0.7)
- [ ] Sensitivity analysis of β1, β2, β3 weights

---

## Phase 5 — Backend API Development
**Duration:** Weeks 16–19  
**Goal:** Wrap the full pipeline in a production-ready REST API using FastAPI, Celery, Redis, and PostgreSQL.

---

### 5.1 FastAPI Application Structure

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import analyze, scores, nodes
from api.db.session import engine, Base

app = FastAPI(
    title="Bot-Aware Influence Scoring API",
    description="Graph-based bot detection and influence scoring for social networks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    # Load GAT models into memory once at startup
    from api.ml_loader import load_models
    load_models()

app.include_router(analyze.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(nodes.router, prefix="/api/v1")
```

---

### 5.2 API Endpoints Reference

#### POST `/api/v1/analyze`

Accepts a custom graph as JSON and runs the full pipeline.

**Request body:**
```json
{
  "nodes": [
    {
      "id": "user_001",
      "account_age_days": 1200,
      "followers_count": 5000,
      "friends_count": 300,
      "statuses_count": 2400,
      "posting_frequency": 2.0,
      "follower_following_ratio": 16.7
    }
  ],
  "edges": [
    {"source": "user_001", "target": "user_002", "type": "follows", "count": 1, "last_date": "2024-11-01"}
  ],
  "config": {
    "tau": 0.5,
    "alpha": 0.6,
    "beta1": 0.333, "beta2": 0.333, "beta3": 0.334,
    "n_ic_simulations": 500
  }
}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "queued",
  "estimated_duration_seconds": 120
}
```

#### GET `/api/v1/jobs/{job_id}`

Poll job status and retrieve results.

**Response (completed):**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "results": {
    "bots_detected": 142,
    "nodes_retained": 1208,
    "pct_removed": 10.5,
    "top_influencers": [
      {"node_id": "user_045", "score": 0.98, "pagerank": 0.021, "authority": 0.87, "ic_reach": 342},
      {"node_id": "user_012", "score": 0.94, "pagerank": 0.018, "authority": 0.79, "ic_reach": 298}
    ],
    "rank_displacement": {
      "top_k": 50,
      "pct_displaced": 44.0,
      "kendalls_tau": 0.61,
      "spearman_r": 0.73
    }
  }
}
```

#### GET `/api/v1/scores/{dataset}`

Return precomputed influence scores for a named dataset.

**Query parameters:**
- `top_k` (int, default 100): Return top-k nodes only
- `min_score` (float, default 0.0): Filter by minimum φv
- `sort_by` (string): `composite`, `pagerank`, `authority`, `ic_reach`
- `graph_type` (string): `raw` or `sanitized`

#### GET `/api/v1/nodes/{node_id}/bot-probability`

Returns bot classification details for a specific node.

**Response:**
```json
{
  "node_id": "user_123",
  "bot_probability": 0.87,
  "is_bot": true,
  "top_suspicious_neighbors": ["user_456", "user_789"],
  "feature_breakdown": {
    "posting_frequency": 8.4,
    "content_diversity": 0.03,
    "temporal_burstiness": 2.1,
    "follower_following_ratio": 0.02
  }
}
```

#### GET `/api/v1/ranking-shift`

Return rank displacement statistics for a dataset comparison.

#### WebSocket `/api/v1/ws/jobs/{job_id}`

Stream live progress for long-running IC simulations:
```json
{"event": "progress", "step": "ic_simulation", "pct_complete": 45, "message": "Running IC simulations (450/1000 nodes)"}
{"event": "completed", "job_id": "abc123"}
```

---

### 5.3 Celery Task Example

```python
# api/tasks/celery_tasks.py
from celery import Celery

celery_app = Celery(
    'bot_influence',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task(bind=True)
def run_full_pipeline(self, graph_data: dict, config: dict):
    """
    Long-running task: graph build → GAT inference → sanitize → score.
    Updates task state for WebSocket polling.
    """
    self.update_state(state='PROGRESS', meta={'step': 'graph_construction', 'pct': 10})
    data = build_graph_from_dict(graph_data, config)

    self.update_state(state='PROGRESS', meta={'step': 'gat_inference', 'pct': 30})
    bot_probs = run_gat_inference(data)

    self.update_state(state='PROGRESS', meta={'step': 'sanitization', 'pct': 50})
    clean_data, stats = sanitize_graph(data, bot_probs, tau=config['tau'])

    self.update_state(state='PROGRESS', meta={'step': 'influence_scoring', 'pct': 60})
    pr = compute_pagerank(clean_data)
    hubs, auth = compute_hits(clean_data)

    self.update_state(state='PROGRESS', meta={'step': 'ic_simulation', 'pct': 70})
    ic = compute_ic_reach(clean_data, n_simulations=config.get('n_ic_simulations', 500))

    self.update_state(state='PROGRESS', meta={'step': 'composite_score', 'pct': 90})
    scores = compute_composite_scores(pr, auth, ic,
                                       config['beta1'], config['beta2'], config['beta3'])

    return {'scores': scores, 'stats': stats}
```

---

### 5.4 Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/botinfluence
      - REDIS_URL=redis://redis:6379/0
      - MODEL_PATH=/app/models
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    depends_on:
      - db
      - redis

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A api.tasks.celery_tasks worker --loglevel=info --concurrency=2
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/botinfluence
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    depends_on:
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=botinfluence
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Start everything:**
```bash
docker-compose up --build
```

**API will be available at:** `http://localhost:8000`  
**Auto-generated API docs:** `http://localhost:8000/docs`

---

### Phase 5 Deliverables Checklist

- [ ] FastAPI app with all 6 endpoints implemented
- [ ] Celery task for long-running pipeline jobs
- [ ] Docker Compose configuration for API + worker + Redis + PostgreSQL
- [ ] Auto-generated OpenAPI documentation at `/docs`
- [ ] Integration tests with pytest covering all endpoints
- [ ] Model loading and caching at startup

---

## Phase 6 — Frontend UI & Visualization Dashboard
**Duration:** Weeks 19–24  
**Goal:** Build a React dashboard that makes the full analysis pipeline accessible and visual.

---

### 6.1 Project Initialization

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# UI and state
npm install @tanstack/react-query zustand
npm install tailwindcss @tailwindcss/forms autoprefixer
npx tailwindcss init -p

# Visualization
npm install d3 recharts

# Component library
npm install @radix-ui/react-slider @radix-ui/react-tabs
npm install lucide-react
```

---

### 6.2 UI Views Specification

#### View 1: Graph Explorer

An interactive force-directed visualization of the social network.

**Features:**
- Color nodes by bot probability: red gradient = high bot probability, green = genuine
- Node size proportional to composite influence score φv
- Edge thickness proportional to edge weight wuv
- Click a node to open the Bot Audit Panel (View 4)
- Toggle between raw graph and sanitized graph views
- Filter controls: show only top-K nodes by influence (required for large graphs)
- Zoom, pan, and drag nodes

**Implementation notes:**
- Use D3.js force simulation with `d3.forceLink()`, `d3.forceManyBody()`, `d3.forceCenter()`
- For graphs >5000 nodes: request server-side top-500 subgraph before rendering
- Use canvas renderer (`d3-canvas`) for graphs >2000 nodes for performance
- SVG renderer for smaller graphs (better interaction handling)

#### View 2: Influence Leaderboard

A sortable, filterable table of the top influencers.

**Columns:**

| Column | Description |
|---|---|
| Rank | Position in current ranking |
| Node ID | Account identifier |
| φv score | Composite influence score (0–1) |
| PageRank | PR authority score |
| HITS authority | Kleinberg authority score |
| IC reach | Expected cascade size |
| Bot prob | pv from GAT |
| Rank shift | Change vs raw graph ranking (Δ with arrow) |

**Features:**
- Toggle between raw and sanitized graph rankings
- Highlighted rows where rank shifted by >10 positions
- Export to CSV
- Pagination (50 rows per page)

#### View 3: Before/After Ranking Comparison

**Features:**
- Side-by-side bar chart: top-20 influencers in raw vs sanitized graph
- Animated rank displacement arrows connecting same accounts across both charts
- Summary statistics: Kendall's τ, Spearman ρ, % top-k displaced
- Highlight nodes that entered/exited the top-20 after sanitization

#### View 4: Bot Audit Panel

Opened when clicking a node in the Graph Explorer.

**Displays:**
- Bot probability gauge (semicircle, 0–1)
- Classification label (Bot / Genuine) with confidence
- Top 5 suspicious neighbors with their own bot probabilities
- Feature breakdown table: which features most influenced the classification
- Neighborhood visualization: small graph showing the node and its direct neighbors, colored by bot probability

#### View 5: Upload & Analyze

**Flow:**
1. Drag-and-drop zone for CSV edge list + JSON node features
2. Validation feedback (column names, data types, format errors)
3. Configuration panel with sliders for τ, α, β1, β2, β3
4. Submit → WebSocket progress bar showing pipeline stages
5. Results automatically populate Views 1–4

**Expected file formats:**

Edge list CSV:
```csv
source,target,type,count,last_date
user_001,user_002,follows,1,2024-11-01
user_001,user_003,mentions,5,2024-11-15
```

Node features JSON:
```json
[
  {"id": "user_001", "followers_count": 5000, "friends_count": 300, "statuses_count": 2400, ...},
  {"id": "user_002", ...}
]
```

#### View 6: Metric Controls Panel

Persistent sidebar panel:

- **τ slider** (0.1–0.9): Bot detection threshold. Lower = more aggressive removal.
- **α slider** (0.0–1.0): Edge weight balance between frequency and recency.
- **β1, β2, β3 sliders** (0–1, constrained to sum = 1): Composite score weights for PageRank, HITS, IC.
- All changes trigger debounced API calls (300ms delay) to recompute scores
- Reset to defaults button

---

### 6.3 WebSocket Integration for Live Progress

```typescript
// hooks/useJobProgress.ts
import { useState, useEffect, useRef } from 'react';

interface JobProgress {
  step: string;
  pct_complete: number;
  message: string;
}

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress] = useState<JobProgress | null>(null);
  const [completed, setCompleted] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;

    wsRef.current = new WebSocket(`ws://localhost:8000/api/v1/ws/jobs/${jobId}`);

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'progress') {
        setProgress({
          step: data.step,
          pct_complete: data.pct_complete,
          message: data.message
        });
      } else if (data.event === 'completed') {
        setCompleted(true);
        wsRef.current?.close();
      }
    };

    return () => wsRef.current?.close();
  }, [jobId]);

  return { progress, completed };
}
```

---

### 6.4 Large Graph Rendering Strategy

Rendering 100,000+ nodes directly in the browser is not feasible. Use this tiered approach:

| Graph size | Strategy |
|---|---|
| < 1,000 nodes | Full SVG render with D3 force simulation |
| 1,000–10,000 nodes | Request server-side top-1000 by influence; SVG render |
| 10,000–100,000 nodes | Request server-side top-500; use Canvas renderer |
| > 100,000 nodes | Static layout from server (pre-computed positions); WebGL with Three.js or PixiJS |

Always add a "Show top N" dropdown (options: 100, 500, 1000, all) so users can control rendering density.

---

### Phase 6 Deliverables Checklist

- [ ] React 18 + TypeScript + Vite project initialized
- [ ] All 6 views implemented and connected to backend API
- [ ] Interactive D3 force-directed graph explorer
- [ ] Influence leaderboard with rank shift highlighting
- [ ] Before/after comparison view with animated rank displacement
- [ ] WebSocket progress bar for long-running jobs
- [ ] Custom graph upload and analysis flow
- [ ] Responsive layout working on desktop and tablet

---

## Complete Tech Stack Reference Card

### ML & Graph Layer
```
Python 3.10+          Core language
PyTorch 2.x           Deep learning
PyTorch Geometric     GNN framework (GATConv, HeteroConv, HeteroData)
scikit-learn          Preprocessing, baselines, evaluation metrics
XGBoost               Feature-engineering baseline
NetworkX 3.x          PageRank, HITS, graph algorithms
scipy                 Sparse matrix operations for large graphs
numpy                 Numerical computation
pandas                Data loading, EDA, manipulation
joblib                Parallel IC Monte Carlo simulations
torchmetrics          F1, AUC-ROC during training
CUDA 12.x             GPU acceleration
```

### Tracking & Data Ops
```
MLflow or W&B         Experiment tracking, hyperparameter logging
DVC                   Large dataset versioning
Git + GitHub          Source code version control
Jupyter               EDA notebooks
```

### Backend API
```
FastAPI               REST API framework (async Python)
uvicorn               ASGI server
Celery                Async task queue
Redis                 Celery broker + result cache
PostgreSQL            Persistent storage
SQLAlchemy            ORM
pydantic              Request/response validation
Docker + compose      Containerization
pytest                Testing
```

### Frontend
```
React 18              UI framework
TypeScript            Type safety
Vite                  Build tool
TanStack Query        Server state management
D3.js                 Force-directed graph visualization
Recharts              Bar, scatter, line charts
Tailwind CSS          Styling
shadcn/ui             Accessible component library
Zustand               Client-side state management
WebSocket             Real-time progress streaming
```

---

## Key Equations Reference

| Name | Formula |
|---|---|
| Edge weight | `w_uv = α · f_uv + (1−α) · r_uv` |
| GAT attention | `e_vu = LeakyReLU(a^T [W·x_v ∥ W·x_u])` |
| Attention normalization | `α_vu = exp(e_vu) / Σ_{k∈N(v)} exp(e_vk)` |
| Updated node embedding | `h_v = σ(Σ_{u∈N(v)} α_vu · W·x_u)` |
| Bot probability | `p_v = exp(w_bot^T h_v) / Σ_c exp(w_c^T h_v)` |
| PageRank | `PR(v) = (1−d)/|V'| + d · Σ_{u∈N⁻(v)} PR(u)/|N⁺(u)|` |
| HITS reinforcement | `a_v = Σ h_u` , `h_v = Σ a_u` (iterated to convergence) |
| Composite score | `φ_v = N(β1·PR(v) + β2·a_v + β3·IC(v))` |

---

## Common Issues & Solutions

| Problem | Cause | Solution |
|---|---|---|
| CUDA out of memory | Full graph too large for GPU | Use mini-batch training with `NeighborLoader` from PyG |
| Low F1 despite good accuracy | Class imbalance (bots are minority) | Use `class_weight='balanced'`, weighted sampling, focal loss |
| IC simulation too slow | O(N × simulations) complexity | Parallelize with joblib, reduce n_simulations, use CELF approx |
| PageRank doesn't converge | Dangling nodes (no outgoing edges) | Add self-loops or use `dangling` parameter in NetworkX |
| Frontend graph renderer freezes | Too many SVG nodes | Switch to canvas renderer, limit to top-K nodes |
| Bot removal removes too many nodes | τ too low | Raise τ to 0.6–0.7, plot precision-recall curve to choose optimal τ |

---

*Generated from: Bot-Aware Influence Scoring in Social Networks using GNNs (2026)*  
*Roadmap covers: Environment setup → Graph construction → GAT training → Influence scoring → Backend API → Frontend dashboard*
