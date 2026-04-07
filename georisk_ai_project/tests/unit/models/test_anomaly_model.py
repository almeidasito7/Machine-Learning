import numpy as np
import pandas as pd

from app.models.anomaly import detect_anomalies

class _FakeAnomalyModel:
    def decision_function(self, X):
        return np.array([0.25, -0.5], dtype=float)

    def predict(self, X):
        return np.array([1, -1], dtype=int)

class _IdentityScaler:
    def transform(self, X):
        return X


def test_detect_anomalies_returns_preds_and_inverted_scores(monkeypatch):
    monkeypatch.setattr("app.models.anomaly.load_anomaly_detector", lambda: _FakeAnomalyModel())
    monkeypatch.setattr("app.models.anomaly.load_anomaly_scaler", lambda: _IdentityScaler())

    df = pd.DataFrame(
        {
            "feature_1": [0.1, 0.2],
            "feature_2": [0.0, 0.3],
        }
    )

    preds, scores = detect_anomalies(df)

    assert preds.tolist() == [1, -1]
    assert scores.tolist() == [-0.25, 0.5]
