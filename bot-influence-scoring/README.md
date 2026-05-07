# BotScope — Bot-Aware Influence Scoring

Ever wonder whether the most "influential" accounts on Twitter are actually real people? This project answers that question rigorously. It trains a neural network to detect bots in a social network, removes them from the graph, and then re-ranks everyone by their true influence — exposing how much bots distort the leaderboard.

The result is a full-stack system: a trained AI model, a REST API, and an interactive dashboard where you can explore the network, audit individual accounts, and compare influence rankings before and after bot removal.

---

## What this project does, in plain English

1. **Loads a real Twitter dataset** (Cresci-2017) containing ~11,000 accounts — a mix of genuine users and known bots.

2. **Builds a social graph** where nodes are accounts and edges are interactions (mentions, retweets). Each node carries 18 hand-crafted features like follower count, tweet frequency, and account age.

3. **Trains a Graph Attention Network (GAT)** — a type of neural network that understands graph structure — to classify every account as a bot or a human. It achieves **98.1% accuracy** and **0.978 F1 score** on the test set.

4. **Sanitizes the graph** by removing accounts the model flags as bots (above a configurable confidence threshold τ).

5. **Computes influence scores** on both the raw and the sanitized graph using three metrics: PageRank, HITS authority, and Independent Cascade (IC) reach. These are combined into a single composite score φᵥ.

6. **Serves everything via a REST API** (FastAPI) so that any frontend or script can query bot probabilities, influence rankings, and before/after comparisons.

7. **Visualizes it all** in a React dashboard with a live force-directed network map, a sortable leaderboard, and side-by-side ranking charts.

---

## Project structure

```
bot-influence-scoring/
├── data/
│   └── cresci-2017/
│       ├── raw/           # Original CSV files
│       └── processed/     # Precomputed graph + bot probabilities
├── src/
│   ├── graph/
│   │   ├── builder.py     # Builds the heterogeneous PyG graph
│   │   └── features.py    # Extracts 18 node features
│   ├── models/
│   │   └── gat.py         # BotAwareGAT model definition
│   ├── training/
│   │   ├── trainer.py     # Training loop with early stopping
│   │   └── evaluation.py  # Metrics: F1, ROC-AUC, confusion matrix
│   ├── influence/         # PageRank, HITS, IC simulation, composite score
│   └── utils/
├── api/
│   ├── main.py            # FastAPI app entry point
│   ├── routers/
│   │   ├── scores.py      # GET /api/v1/scores — leaderboard endpoint
│   │   └── nodes.py       # GET /api/v1/nodes/{id} — per-account detail
│   ├── db/
│   │   └── session.py     # In-memory cache of precomputed scores
│   └── schemas/           # Pydantic request/response models
├── frontend/              # React + TypeScript dashboard
│   └── src/
│       ├── views/         # 6 main pages
│       ├── components/    # Reusable UI + chart components
│       ├── hooks/         # Data fetching + WebSocket hooks
│       └── store/         # Zustand global state
├── notebooks/
│   ├── 05_gat_training.py # Standalone training script
│   └── 06_baselines.py    # Logistic regression / XGBoost baselines
├── models/
│   └── gat_cresci2017.pt  # Saved trained model weights
└── pyproject.toml
```

---

## Requirements

| Tool | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| PyTorch | 2.x |
| PyTorch Geometric | 2.x |
| Apple Silicon (MPS) or CUDA GPU | Recommended for training |

---

## Setup

### 1. Clone the repo

```bash
git clone <repo-url>
cd bot-influence-scoring
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install Python dependencies

```bash
pip install -e .
```

If you are on Apple Silicon, install PyTorch with MPS support:

```bash
pip install torch torchvision torchaudio
pip install torch-geometric
```

For CUDA (NVIDIA GPU), follow the [PyTorch install guide](https://pytorch.org/get-started/locally/) to pick the right wheel.

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Running the system

The system has two independent servers — the Python backend and the React frontend. You need both running at the same time.

### Start the backend API

Open a terminal in the `bot-influence-scoring/` directory and run:

```bash
PYTHONPATH=. .venv/bin/uvicorn api.main:app --reload --port 8000
```

> **Important:** Always use `.venv/bin/uvicorn` rather than a globally installed `uvicorn`. The project dependencies (`torch`, `torch-geometric`, etc.) are installed inside `.venv/`, and the system Python won't find them. If you activate the venv first (`source .venv/bin/activate`), you can use `uvicorn` directly.

The API will be live at `http://localhost:8000`. You can explore all endpoints interactively at `http://localhost:8000/docs`.

### Start the frontend dashboard

Open a second terminal:

```bash
cd frontend
npm run dev
```

The dashboard will open at `http://localhost:5173`.

---

## What you'll see in the dashboard

The sidebar on the left lets you navigate between six views:

| View | What it shows |
|---|---|
| **Network Graph** | A live, interactive map of the social network. Green nodes are genuine users, red nodes are bots, orange are uncertain. Node size reflects influence score. Click any node to open an audit panel. |
| **Leaderboard** | A sortable table of the top influencers with their composite score, PageRank, HITS authority, IC reach, and bot probability. Toggle between raw and sanitized rankings. Export to CSV. |
| **Before / After** | Side-by-side bar charts showing the top 20 influencers in the raw graph vs. the sanitized graph. Summary stats (Kendall's τ, Spearman ρ) quantify how much bot removal reshuffled the rankings. |
| **Upload & Analyze** | Drag-and-drop your own edge list (CSV) and node features (JSON) to run the full pipeline on custom data. A live progress bar tracks each pipeline stage via WebSocket. |
| **Settings** | Adjust the bot threshold τ, edge weight decay α, and the β₁/β₂/β₃ weights that blend PageRank, HITS, and IC reach into the composite score. |

---

## Training the model yourself

If you want to retrain the GAT from scratch (the pretrained weights are already in `models/gat_cresci2017.pt`):

```bash
PYTHONPATH=. python notebooks/05_gat_training.py
```

Training runs on MPS (Apple Silicon) or CUDA automatically if available, otherwise CPU. With MPS it takes about 5–10 minutes. The script uses early stopping with patience=50 on validation F1, so it will stop automatically when the model converges.

Expected results after training:

| Metric | Value |
|---|---|
| Test Accuracy | 98.1% |
| Test F1 (macro) | 0.978 |
| Test ROC-AUC | 0.993 |

---

## Running baselines

To compare the GAT against traditional ML approaches (logistic regression, XGBoost):

```bash
PYTHONPATH=. python notebooks/06_baselines.py
```

---

## Key API endpoints

Once the backend is running, these are the main endpoints:

```
GET  /api/v1/scores/cresci-2017?top_k=100&graph_type=raw
     → Top-K influencers from the raw or sanitized graph

GET  /api/v1/nodes/{node_idx}/bot-probability
     → Bot probability + feature breakdown for a single account

GET  /api/v1/comparison/cresci-2017
     → Before/after ranking displacement statistics

POST /api/v1/analyze
     → Submit a custom graph (CSV edges + JSON nodes) for analysis

WS   /api/v1/ws/jobs/{job_id}
     → WebSocket stream of real-time pipeline progress
```

Full interactive docs: `http://localhost:8000/docs`

---

## Dataset

This project uses the **Cresci-2017** dataset, a widely used benchmark for Twitter bot detection research. It contains 11,017 accounts:

- 3,474 genuine users (31.5%)
- 7,543 bots (68.5%) across several bot categories (social spambots, traditional spambots, fake followers)

The dataset is loaded from `data/cresci-2017/raw/`. The preprocessed graph (node features, edge index, labels) is cached at `data/cresci-2017/processed/hetero_graph.pt` and bot probabilities at `data/cresci-2017/processed/bot_probabilities.pt`.

---

## How the influence score works

Each account gets a composite influence score φᵥ:

```
φᵥ = β₁ · PageRank(v) + β₂ · HITS_Authority(v) + β₃ · IC_Reach(v)
```

Where:
- **PageRank** — how many important accounts point to you
- **HITS Authority** — how authoritative you are in the information flow
- **IC Reach** — how many people you can reach in an information cascade simulation
- **β₁, β₂, β₃** — configurable weights (default: equal thirds, must sum to 1)

Before computing φᵥ, all accounts with bot probability ≥ τ (default: 0.5) are removed from the graph. This is the "sanitization" step. The sliders in the dashboard let you change τ and the β weights live and see how the rankings shift.
