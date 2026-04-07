import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
)


def evaluate_anomaly(y_true, y_pred):
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def evaluate_failure(y_true, y_prob, threshold: float = 0.5):
    y_pred = (y_prob >= threshold).astype(int)

    # Guard against ROC AUC errors when only one class is present.
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    tp = int(cm[1][1])
    tn = int(cm[0][0])
    fp = int(cm[0][1])
    fn = int(cm[1][0])

    return {
        "roc_auc": float(roc_auc),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": cm,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "pred_positive_rate": float((y_pred == 1).mean()) if len(y_pred) else 0.0,
    }


def evaluate_risk(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    if len(y_true) == 0:
        return {"mae": 0.0, "rmse": 0.0}

    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }
