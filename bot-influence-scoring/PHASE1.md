# Phase 1: Project Initialization & Data Preparation

This document summarizes the work completed during Phase 1 of the Bot-Aware Influence Scoring project.

## 1. Project Directory Structure
Implemented the modular architecture as defined in the roadmap:
- `data/cresci-2017/`: Raw and processed dataset storage.
- `src/`: Core logic (graph, models, training, influence, utils).
- `api/`: FastAPI backend components.
- `notebooks/`: Prototyping and EDA scripts.
- `models/`: Model checkpoints.
- `tests/`: Unit and integration tests.

## 2. Environment Setup
- **Python Virtual Environment**: Created in `.venv/`.
- **Dependencies**: Managed via `pyproject.toml`, including:
    - `torch`, `torch-geometric` (GNN framework)
    - `pandas`, `numpy`, `scipy` (Data processing)
    - `scikit-learn`, `xgboost` (Baselines)
    - `fastapi`, `uvicorn`, `celery`, `redis` (Backend)
    - `dvc`, `dvc-gdrive` (Data versioning)
- **Hardware Acceleration**: Verified **Metal (MPS)** availability for Apple Silicon GPU training.

## 3. Data Acquisition & Processing
- **Dataset**: Cresci-2017 (Social Spambots).
- **Extraction**: Unzipped and organized sub-datasets:
    - `genuine_accounts`
    - `social_spambots_1/2/3`
    - `traditional_spambots_1/2/3/4`
- **Consolidation**: Aggregated 11,017 users into a single labeled dataset (`data/cresci-2017/processed/users_labeled.csv`).
    - Class 0 (Genuine): 3,474
    - Class 1 (Bot): 7,543

## 4. Exploratory Data Analysis (EDA)
Created `notebooks/01_EDA_cresci.py` which generated the following insights:
- **Class Distribution**: Identified a significant presence of bots in the dataset.
- **Feature Analysis**: Analyzed distributions of `followers_count`, `friends_count`, `statuses_count`, etc.
- **Missing Values**: Identified high missingness in fields like `geo_enabled` and `default_profile`.
- **Correlations**: Mapped relationships between account metadata features.

## 5. Version Control Initialization
- **Git**: Repository initialized with `.gitignore`.
- **DVC**: Initialized for tracking large data files and model checkpoints.

---
**Next Step**: Phase 2 — Heterogeneous Graph Construction (Weeks 3–6).
