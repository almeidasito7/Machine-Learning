import numpy as np
import pandas as pd
import pytest

from app.models.predictor import predict_failure_probability


class _IdentityScaler:
    def transform(self, X):
        return X


class _FakeBinaryModel:
    def __init__(self, classes_):
        self.classes_ = np.array(classes_, dtype=int)

    def predict_proba(self, X):
        p1 = np.linspace(0.1, 0.9, num=len(X))
        p0 = 1.0 - p1

        if self.classes_.tolist() == [0, 1]:
            return np.vstack([p0, p1]).T
        if self.classes_.tolist() == [1, 0]:
            return np.vstack([p1, p0]).T
        raise ValueError("unsupported classes")


class _FakeSingleClassModel:
    def __init__(self, class_value):
        self.classes_ = np.array([class_value], dtype=int)

    def predict_proba(self, X):
        return np.ones((len(X), 1), dtype=float)


def test_predict_failure_probability_selects_class_1_column(monkeypatch):
    monkeypatch.setattr(
        "app.models.predictor.load_failure_predictor",
        lambda: (_FakeBinaryModel([1, 0]), _IdentityScaler()),
    )
    monkeypatch.setattr(
        "app.models.predictor.load_metadata",
        lambda: {"features": ["feature_1", "feature_2"]},
    )

    df = pd.DataFrame({"feature_1": [0.0, 1.0], "feature_2": [1.0, 0.0]})
    probs = predict_failure_probability(df)

    assert probs.shape == (2,)
    assert (probs >= 0).all() and (probs <= 1).all()
    assert probs[0] < probs[1]


def test_predict_failure_probability_handles_missing_features(monkeypatch):
    monkeypatch.setattr(
        "app.models.predictor.load_failure_predictor",
        lambda: (_FakeBinaryModel([0, 1]), _IdentityScaler()),
    )
    monkeypatch.setattr(
        "app.models.predictor.load_metadata",
        lambda: {"features": ["feature_1", "feature_2", "feature_3"]},
    )

    df = pd.DataFrame({"feature_1": [0.0, 1.0], "feature_2": [1.0, 0.0]})
    probs = predict_failure_probability(df)

    assert probs.shape == (2,)
    assert (probs >= 0).all() and (probs <= 1).all()


def test_predict_failure_probability_handles_single_class_model(monkeypatch):
    monkeypatch.setattr(
        "app.models.predictor.load_failure_predictor",
        lambda: (_FakeSingleClassModel(1), _IdentityScaler()),
    )
    monkeypatch.setattr(
        "app.models.predictor.load_metadata",
        lambda: {"features": ["feature_1"]},
    )

    df = pd.DataFrame({"feature_1": [0.0, 1.0, 2.0]})

    with pytest.raises(ValueError):
        predict_failure_probability(df)
