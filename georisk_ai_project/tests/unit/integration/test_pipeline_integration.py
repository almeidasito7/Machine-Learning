import numpy as np
import pandas as pd
import pytest

from app.services.pipeline.inference_pipeline import inference_pipeline


def test_inference_pipeline_aggregates_structures(monkeypatch):
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=6, freq="h"),
            "structure_id": [1, 1, 2, 2, 3, 3],
            "target": [0, 1, 0, 0, 1, 1],
            "failure": [0, 1, 0, 0, 1, 0],
            "anomaly": [0, 0, 0, 0, 0, 1],
            "feature_1": [0.1, 0.2, 0.3, 0.1, 0.9, 0.8],
            "feature_2": [0.0, 0.1, 0.2, 0.2, 0.7, 0.6],
        }
    )

    monkeypatch.setattr("app.services.pipeline.inference_pipeline.load_dataset", lambda **_: df)
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.load_metadata",
        lambda: {"features": ["feature_1", "feature_2"]},
    )
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.detect_anomalies",
        lambda X: (np.array([1, 1, 1, 1, 1, 1]), np.array([0.1, 0.2, 0.05, 0.0, 0.8, 0.7])),
    )
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.predict_failure_probability",
        lambda X: np.array([0.05, 0.10, 0.20, 0.15, 0.90, 0.85]),
    )
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.generate_narrative",
        lambda data: "narrative",
    )

    result = inference_pipeline(
        generate_narrative_flag=True,
        dataset_type="external",
        max_structures=2,
        include_raw_data=True,
    )

    assert result["total_structures"] == 2
    assert result["high_risk_count"] + result["medium_risk_count"] + result["low_risk_count"] == 2
    assert len(result["structures"]) == 2
    assert isinstance(result["insight"], str)
    assert "raw_preview" in result


def test_inference_pipeline_requires_target(monkeypatch):
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
            "structure_id": [1, 1],
            "feature_1": [0.1, 0.2],
        }
    )

    monkeypatch.setattr("app.services.pipeline.inference_pipeline.load_dataset", lambda **_: df)
    monkeypatch.setattr(
        "app.services.pipeline.inference_pipeline.load_metadata",
        lambda: {"features": ["feature_1"]},
    )

    with pytest.raises(ValueError):
        inference_pipeline(generate_narrative_flag=False)
