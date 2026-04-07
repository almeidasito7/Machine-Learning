from pathlib import Path
import joblib
import pandas as pd

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MODEL_PATH = settings.model_path / "anomaly_model.pkl"
SCALER_PATH = settings.model_path / "anomaly_scaler.pkl"


def get_feature_columns(df: pd.DataFrame):
    cols = [c for c in df.columns if c.startswith("feature_")]
    if not cols:
        raise ValueError("No feature_* columns found for anomaly detection")
    return cols


def train_anomaly_detector(df: pd.DataFrame):
    logger.info("Training anomaly detector...")

    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=settings.anomaly_contamination,
        random_state=42,
    )

    model.fit(X_scaled)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    logger.info("Anomaly model trained and saved")

    return model


def load_anomaly_detector():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Anomaly model not found. Train first.")

    return joblib.load(MODEL_PATH)

def load_anomaly_scaler():
    if not SCALER_PATH.exists():
        raise FileNotFoundError("Anomaly scaler not found. Train first.")

    return joblib.load(SCALER_PATH)


def detect_anomalies(df: pd.DataFrame):
    model = load_anomaly_detector()
    scaler = load_anomaly_scaler()

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    X_scaled = scaler.transform(X)

    scores = -model.decision_function(X_scaled)
    preds = model.predict(X_scaled)

    return preds, scores
