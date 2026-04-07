import json
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.config import settings

OUTPUT_PATH = settings.data_path / "external" / "dataset_external.csv"
MODEL_METADATA_PATH = settings.model_path / "model_metadata.json"

NUM_ROWS = 10000
NUM_BATCHES = 10
NUM_STRUCTURES = 10
NUM_SENSORS = 50

rng = np.random.default_rng(42)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

if not MODEL_METADATA_PATH.exists():
    raise FileNotFoundError(
        f"Model metadata not found at {MODEL_METADATA_PATH}. Run /train first."
    )

with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

feature_cols = metadata.get("features", [])
if not feature_cols:
    raise ValueError("No features found in metadata")

base_feature_cols = sorted([c for c in feature_cols if re.fullmatch(r"feature_\d+", c)])
if not base_feature_cols:
    base_feature_cols = [f"feature_{i}" for i in range(1, 129)]

NUM_BASE_FEATURES = len(base_feature_cols)


def generate_dataset():
    n = NUM_ROWS

    idx = np.arange(n)
    batch = idx % NUM_BATCHES
    structure_id = idx % NUM_STRUCTURES
    sensor_id = idx % NUM_SENSORS
    timestamp = pd.date_range("2024-01-01", periods=n, freq="h")

    structure_factor = rng.normal(0, 1.0, NUM_STRUCTURES)
    sensor_factor = rng.normal(0, 0.6, NUM_SENSORS)

    t = np.linspace(0, 1, n, dtype=float)
    drift = (
        0.03 * np.sin(2 * np.pi * batch / max(NUM_BATCHES, 1))
        + 0.02 * np.sin(2 * np.pi * t)
        + 0.01 * structure_factor[structure_id]
        + 0.008 * sensor_factor[sensor_id]
        + rng.normal(0, 0.01, n)
    )

    temperature = 25 + 2 * np.sin(2 * np.pi * t) + rng.normal(0, 1.5, n)
    pressure = (
        200
        + 2.0 * structure_id
        + 10 * np.tanh(drift * 5)
        + 0.8 * (temperature - 25)
        + rng.normal(0, 8, n)
    )
    displacement = (
        4
        + 2.5 * np.tanh(drift * 6)
        + 0.015 * (pressure - 200)
        + rng.normal(0, 0.9, n)
    )
    strain = (
        displacement * 0.01
        + 0.0004 * (pressure - 200)
        + 0.005 * np.tanh(drift * 4)
        + rng.normal(0, 0.006, n)
    )

    base = rng.normal(0, 1, (n, NUM_BASE_FEATURES))
    feature_values = (
        np.tanh(base * 0.8 + drift[:, None] * 3)
        + rng.normal(0, 0.05, (n, NUM_BASE_FEATURES))
        + 0.02 * structure_id[:, None]
    )

    if NUM_BASE_FEATURES >= 10:
        feature_values[:, :10] += (strain * 15)[:, None] + rng.normal(0, 0.05, (n, 10))
    if NUM_BASE_FEATURES >= 20:
        feature_values[:, 10:20] += (displacement / 5)[:, None] + rng.normal(0, 0.05, (n, 10))
    if NUM_BASE_FEATURES >= 30:
        feature_values[:, 20:30] += (pressure / 300)[:, None] + rng.normal(0, 0.05, (n, 10))

    desired_anomaly_rate = 0.03
    desired_failure_rate = 0.09

    anomaly_score = (
        np.abs(feature_values[:, : min(10, NUM_BASE_FEATURES)].mean(axis=1))
        + np.abs(drift) * 2
        + rng.normal(0, 0.3, n)
    )
    failure_score = (
        0.8 * np.tanh((strain - np.median(strain)) / (np.std(strain) + 1e-6))
        + 0.6 * np.tanh((displacement - np.median(displacement)) / (np.std(displacement) + 1e-6))
        + 0.3 * np.tanh((pressure - np.median(pressure)) / (np.std(pressure) + 1e-6))
        + rng.normal(0, 0.2, n)
    )

    anomaly_threshold = float(np.quantile(anomaly_score, 1 - desired_anomaly_rate))
    failure_threshold = float(np.quantile(failure_score, 1 - desired_failure_rate))

    anomaly = (anomaly_score >= anomaly_threshold).astype(int)
    failure = (failure_score >= failure_threshold).astype(int)

    if anomaly.any():
        m = anomaly.astype(bool)
        feature_values[m] += rng.normal(0.8, 0.4, (int(m.sum()), NUM_BASE_FEATURES))
        displacement[m] += rng.normal(2.5, 1.0, int(m.sum()))
        strain[m] += rng.normal(0.02, 0.01, int(m.sum()))
        pressure[m] += rng.normal(30, 15, int(m.sum()))

    if failure.any():
        m = failure.astype(bool)
        displacement[m] += rng.normal(3.0, 1.2, int(m.sum()))
        strain[m] += rng.normal(0.03, 0.015, int(m.sum()))
        pressure[m] += rng.normal(20, 10, int(m.sum()))

    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    risk_score = (
        0.55 * _sigmoid((displacement - np.quantile(displacement, 0.7)) / 2.0)
        + 0.45 * _sigmoid((strain - np.quantile(strain, 0.7)) / 0.02)
    )
    risk_score = np.clip(risk_score, 0.0, 1.0)

    target = ((anomaly + failure) > 0).astype(int)

    df = pd.DataFrame(
        feature_values,
        columns=base_feature_cols,
    )
    df.insert(0, "sensor_id", sensor_id.astype(int))
    df.insert(0, "structure_id", structure_id.astype(int))
    df.insert(0, "batch", batch.astype(int))
    df.insert(0, "timestamp", timestamp)

    df["displacement_mm"] = displacement
    df["pressure_kpa"] = pressure
    df["strain"] = strain
    df["temperature"] = temperature
    df["anomaly"] = anomaly
    df["failure"] = failure
    df["risk_score"] = risk_score
    df["target"] = target

    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved at: {OUTPUT_PATH}")
    print(f"Shape: {df.shape}")
    print(
        {
            "target_rate": float(df["target"].mean()),
            "anomaly_rate": float(df["anomaly"].mean()),
            "failure_rate": float(df["failure"].mean()),
        }
    )
