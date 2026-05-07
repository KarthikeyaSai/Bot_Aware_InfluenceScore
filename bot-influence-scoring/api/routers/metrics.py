import numpy as np
import torch
import os
from fastapi import APIRouter, HTTPException, Query
from sklearn.metrics import roc_curve, precision_recall_curve, auc

router = APIRouter()

DATASET_PATHS = {
    "cresci-2017": {
        "probs": "data/cresci-2017/processed/bot_probabilities.pt",
        "graph": "data/cresci-2017/processed/hetero_graph.pt",
    },
    "mgtab": {
        "probs": "data/mgtab/processed/bot_probabilities.pt",
        "graph": "data/mgtab/processed/hetero_graph.pt",
    },
}

# Named features for 18-dim Cresci; MGTAB features are anonymous (788-dim)
CRESCI_FEATURE_NAMES = [
    "Account Age (days)", "Followers (log)", "Friends (log)", "Listed (log)",
    "Favourites (log)", "Follower/Following Ratio", "Profile Completeness",
    "Default Profile", "Default Profile Image", "Geo Enabled", "Verified",
    "Protected", "Name Length", "Screen Name Length", "Description Length",
    "Posting Frequency", "Retweet Ratio", "URL Ratio",
]

_cache: dict = {}


def _load(dataset: str = "cresci-2017"):
    if dataset in _cache:
        return _cache[dataset]
    paths = DATASET_PATHS.get(dataset)
    if not paths:
        return {}
    if not os.path.exists(paths["probs"]) or not os.path.exists(paths["graph"]):
        return {}
    probs = torch.load(paths["probs"], weights_only=False).numpy()
    g = torch.load(paths["graph"], weights_only=False)
    labels = g["user"].y.numpy()
    features = g["user"].x.numpy()
    _cache[dataset] = {"probs": probs, "labels": labels, "features": features}
    return _cache[dataset]


@router.get("/")
async def get_metrics(dataset: str = Query("cresci-2017")):
    data = _load(dataset)
    if not data:
        raise HTTPException(status_code=503, detail=f"Data for '{dataset}' not loaded.")

    probs    = data["probs"]
    labels   = data["labels"]
    features = data["features"]
    preds    = (probs >= 0.5).astype(int)

    # Confusion matrix
    tn = int(((preds == 0) & (labels == 0)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    tp = int(((preds == 1) & (labels == 1)).sum())
    total     = tn + fp + fn + tp
    accuracy  = round((tp + tn) / total * 100, 2)
    precision = round(tp / (tp + fp) * 100, 2) if (tp + fp) else 0
    recall    = round(tp / (tp + fn) * 100, 2) if (tp + fn) else 0
    f1        = round(2 * precision * recall / (precision + recall), 2) if (precision + recall) else 0

    # ROC curve
    fpr_all, tpr_all, _ = roc_curve(labels, probs)
    roc_auc = round(auc(fpr_all, tpr_all), 4)
    idx = np.linspace(0, len(fpr_all) - 1, 200, dtype=int)
    roc_points = [{"fpr": round(float(fpr_all[i]), 4), "tpr": round(float(tpr_all[i]), 4)} for i in idx]

    # PR curve
    prec_all, rec_all, _ = precision_recall_curve(labels, probs)
    pr_auc = round(auc(rec_all, prec_all), 4)
    idx2 = np.linspace(0, len(prec_all) - 1, 200, dtype=int)
    pr_points = [{"precision": round(float(prec_all[i]), 4), "recall": round(float(rec_all[i]), 4)} for i in idx2]

    # Score distribution
    bins = np.linspace(0, 1, 31)
    centers = ((bins[:-1] + bins[1:]) / 2).round(3)
    genuine_hist, _ = np.histogram(probs[labels == 0], bins=bins)
    bot_hist, _     = np.histogram(probs[labels == 1], bins=bins)
    score_dist = [
        {"bin": float(centers[i]), "genuine": int(genuine_hist[i]), "bot": int(bot_hist[i])}
        for i in range(len(centers))
    ]

    # Feature importance — top 18 by correlation (MGTAB has 788 features, show top 18)
    n_features = features.shape[1]
    feat_names = CRESCI_FEATURE_NAMES if n_features == 18 else [f"Feature {i}" for i in range(n_features)]
    importances = []
    for i in range(n_features):
        feat = features[:, i]
        if feat.std() == 0:
            corr = 0.0
        else:
            corr = float(np.corrcoef(feat, labels)[0, 1])
        importances.append({
            "feature": feat_names[i],
            "correlation": round(abs(corr), 4),
            "direction": "bot" if corr > 0 else "genuine",
        })
    importances.sort(key=lambda x: x["correlation"], reverse=True)
    importances = importances[:18]  # show top 18 for any dataset

    return {
        "dataset": dataset,
        "confusionMatrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "summary": {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1, "rocAuc": roc_auc, "prAuc": pr_auc},
        "rocCurve": roc_points,
        "prCurve": pr_points,
        "scoreDist": score_dist,
        "featureImportance": importances,
    }
