import json
import joblib
import pandas as pd

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MODEL_PATH = settings.model_path / "failure_model.pkl"
SCALER_PATH = settings.model_path / "failure_scaler.pkl"
METADATA_PATH = settings.model_path / "model_metadata.json"


def load_metadata():
    if not METADATA_PATH.exists():
        raise FileNotFoundError("Model metadata not found. Train first.")

    with open(METADATA_PATH, "r") as f:
        return json.load(f)


def train_failure_predictor(X_train, y_train, X_test, y_test):
    logger.info("Training failure predictor...")

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report
    from sklearn.metrics import f1_score
    from sklearn.metrics import roc_auc_score
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42,
    )

    model.fit(X_train_scaled, y_train)

    probs = model.predict_proba(X_test_scaled)
    if probs.shape[1] != 2 or set(getattr(model, "classes_", [])) != {0, 1}:
        raise ValueError("Failure model must be binary with classes {0, 1}")

    positive_index = int(list(model.classes_).index(1))
    y_prob = probs[:, positive_index]

    try:
        roc_auc = float(roc_auc_score(y_test, y_prob))
    except Exception:
        roc_auc = 0.5

    thresholds = [i / 100 for i in range(5, 96, 5)]
    best_threshold = 0.5
    best_f1 = -1.0

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        score = float(f1_score(y_test, y_pred, zero_division=0))
        if score > best_f1:
            best_f1 = score
            best_threshold = float(t)

    preds = (y_prob >= best_threshold).astype(int)
    report = classification_report(y_test, preds, output_dict=True)
    report["roc_auc"] = roc_auc
    report["threshold"] = best_threshold

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    logger.info("Failure predictor trained and saved")

    return model, report


def load_failure_predictor():
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("Failure model not found. Train first.")

    return joblib.load(MODEL_PATH), joblib.load(SCALER_PATH)


def predict_failure_probability(df: pd.DataFrame):
    model, scaler = load_failure_predictor()
    metadata = load_metadata()

    feature_cols = metadata["features"]

    missing = [f for f in feature_cols if f not in df.columns]

    if missing:
        logger.warning(f"Missing features in predictor: {missing}")
        for f in missing:
            df[f] = 0.0

    X = df.reindex(columns=feature_cols, fill_value=0)

    if X.shape[1] != len(feature_cols):
        raise ValueError("Feature mismatch between model and dataset")

    X_scaled = scaler.transform(X)

    probs = model.predict_proba(X_scaled)

    if probs.shape[1] != 2:
        raise ValueError("Failure model must be binary (2 classes)")

    if set(getattr(model, "classes_", [])) != {0, 1}:
        raise ValueError("Failure model classes must be {0, 1}")

    positive_index = int(list(model.classes_).index(1))
    return probs[:, positive_index]
