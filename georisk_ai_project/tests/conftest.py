import pytest
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd
import numpy as np


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_df():
    n = 200
    rng = np.random.default_rng(42)

    df = pd.DataFrame(
        {
            **{f"feature_{i}": rng.normal(0, 1, n) for i in range(1, 129)},
            "structure_id": rng.integers(1, 5, n),
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="h"),
        }
    )

    df["anomaly"] = (rng.random(n) < 0.05).astype(int)
    df["failure"] = (rng.random(n) < 0.08).astype(int)
    df["target"] = ((df["anomaly"] + df["failure"]) > 0).astype(int)

    return df
