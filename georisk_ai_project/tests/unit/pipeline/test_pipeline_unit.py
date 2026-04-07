import numpy as np
import pandas as pd

from app.services.pipeline.inference_pipeline import inference_pipeline


def test_inference_pipeline_without_narrative(monkeypatch):
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
            "structure_id": [1, 1],
            "target": [0, 1],
            "feature_1": [0.1, 0.2],
        }
    )

    monkeypatch.setattr("app.services.pipeline.inference_pipeline.load_dataset", lambda **_: df)
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.load_metadata",
        lambda: {"features": ["feature_1"]},
    )
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.detect_anomalies",
        lambda X: (np.array([1, 1]), np.array([0.0, 0.0])),
    )
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.predict_failure_probability",
        lambda X: np.array([0.1, 0.2]),
    )

    result = inference_pipeline(generate_narrative_flag=False)

    assert "structures" in result
    assert result["insight"] is None
