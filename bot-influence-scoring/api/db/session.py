import pandas as pd
import numpy as np
import torch
import os
import networkx as nx

# Per-dataset cache
DATASETS: dict[str, dict] = {
    "cresci-2017": {"influence_df": None, "bot_probs": None, "edges": None, "raw_pagerank": None, "loaded": False},
    "mgtab":       {"influence_df": None, "bot_probs": None, "edges": None, "raw_pagerank": None, "loaded": False},
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

        # Build full graph (all nodes including bots) and compute raw PageRank
        G_raw = nx.DiGraph()
        for s, d, wt in zip(src.tolist(), dst.tolist(), w.tolist()):
            G_raw.add_edge(int(s), int(d), weight=float(wt))
        raw_pr = nx.pagerank(G_raw, alpha=0.85, weight='weight', max_iter=200)

        # Build sanitized graph (genuine nodes only) and compute clean PageRank
        bot_probs_arr = cache.get("bot_probs")
        if bot_probs_arr is not None:
            genuine_set = set(int(i) for i in range(len(bot_probs_arr)) if bot_probs_arr[i] < 0.5)
        else:
            genuine_set = set(G_raw.nodes())
        G_clean = nx.DiGraph()
        for s, d, wt in zip(src.tolist(), dst.tolist(), w.tolist()):
            s, d = int(s), int(d)
            if s in genuine_set and d in genuine_set:
                G_clean.add_edge(s, d, weight=float(wt))
        clean_pr = nx.pagerank(G_clean, alpha=0.85, weight='weight', max_iter=200)

        def _minmax_norm(pr_dict):
            vals = np.array(list(pr_dict.values()))
            lo, hi = vals.min(), vals.max()
            return {n: float((v - lo) / (hi - lo + 1e-12)) for n, v in pr_dict.items()}

        cache["raw_pagerank"]   = _minmax_norm(raw_pr)
        cache["clean_pagerank"] = _minmax_norm(clean_pr)
        print(f"[{name}] PageRank: raw={G_raw.number_of_nodes():,} nodes, "
              f"sanitized={G_clean.number_of_nodes():,} nodes")

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

def get_raw_pagerank(dataset: str = "cresci-2017"):
    return DATASETS.get(dataset, {}).get("raw_pagerank")

def get_clean_pagerank(dataset: str = "cresci-2017"):
    return DATASETS.get(dataset, {}).get("clean_pagerank")

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
