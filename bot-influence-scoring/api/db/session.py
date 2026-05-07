import pandas as pd
import numpy as np
import torch
import os

# Per-dataset cache
DATASETS: dict[str, dict] = {
    "cresci-2017": {"influence_df": None, "bot_probs": None, "edges": None, "loaded": False},
    "mgtab":       {"influence_df": None, "bot_probs": None, "edges": None, "loaded": False},
}

DATASET_PATHS = {
    "cresci-2017": {
        "influence": "data/cresci-2017/processed/influence_results.csv",
        "probs":     "data/cresci-2017/processed/bot_probabilities.pt",
        "graph":     "data/cresci-2017/processed/hetero_graph.pt",
    },
    "mgtab": {
        "influence": "data/mgtab/processed/influence_results.csv",
        "probs":     "data/mgtab/processed/bot_probabilities.pt",
        "graph":     "data/mgtab/processed/hetero_graph.pt",
    },
}


def _load_edges(graph_path: str):
    """Load all edges from a HeteroData graph, vectorised."""
    g = torch.load(graph_path, weights_only=False)
    src_all, dst_all, w_all = [], [], []
    for et in g.edge_types:
        ei = g[et].edge_index.numpy()
        ea = g[et].edge_attr
        w = ea[:, 0].numpy() if ea is not None else np.ones(ei.shape[1], dtype=np.float32)
        src_all.append(ei[0])
        dst_all.append(ei[1])
        w_all.append(w)
    return (
        np.concatenate(src_all),
        np.concatenate(dst_all),
        np.concatenate(w_all),
    )


def load_dataset(name: str):
    if name not in DATASETS:
        return
    cache = DATASETS[name]
    if cache["loaded"]:
        return
    paths = DATASET_PATHS[name]

    if os.path.exists(paths["influence"]):
        cache["influence_df"] = pd.read_csv(paths["influence"])
        print(f"[{name}] Loaded influence results ({len(cache['influence_df'])} rows)")

    if os.path.exists(paths["probs"]):
        cache["bot_probs"] = torch.load(paths["probs"], weights_only=False).numpy()
        print(f"[{name}] Loaded bot probabilities ({len(cache['bot_probs'])} nodes)")

    if os.path.exists(paths["graph"]):
        src, dst, w = _load_edges(paths["graph"])
        cache["edges"] = (src, dst, w)
        print(f"[{name}] Loaded {len(src):,} edges")

    cache["loaded"] = True


def load_precomputed_data():
    for name in DATASETS:
        load_dataset(name)


def get_influence_df(dataset: str = "cresci-2017"):
    return DATASETS.get(dataset, {}).get("influence_df")

def get_bot_probs(dataset: str = "cresci-2017"):
    return DATASETS.get(dataset, {}).get("bot_probs")

def get_edges(dataset: str = "cresci-2017"):
    return DATASETS.get(dataset, {}).get("edges")

def get_dataset_info():
    info = []
    for name, cache in DATASETS.items():
        probs = cache.get("bot_probs")
        df = cache.get("influence_df")
        edges = cache.get("edges")
        if probs is None:
            continue
        labels_path = DATASET_PATHS[name]["graph"]
        try:
            g = torch.load(labels_path, weights_only=False)
            labels = g["user"].y.numpy()
            n_bots = int((labels == 1).sum())
            n_genuine = int((labels == 0).sum())
        except Exception:
            n_bots = n_genuine = 0
        info.append({
            "id": name,
            "nodes": len(probs),
            "bots": n_bots,
            "genuine": n_genuine,
            "edges": int(len(edges[0])) if edges is not None else 0,
            "features": int(g["user"].x.shape[1]) if probs is not None else 0,
            "ready": df is not None,
        })
    return info
