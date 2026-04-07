import pandas as pd
import pytest

from app.services.kpi_aggregator import aggregate


def test_aggregate_basic():
    df = pd.DataFrame(
        {
            "risk_status": ["CRITICAL", "WARNING", "SAFE", "CRITICAL", "SAFE"],
            "risk_score": [0.9, 0.6, 0.1, 0.8, 0.2],
            "failure_probability": [0.9, 0.5, 0.1, 0.7, 0.2],
        }
    )

    result = aggregate(df)

    assert result["total_structures"] == 5
    assert result["critical_risk_count"] == 2
    assert result["warning_risk_count"] == 1
    assert result["safe_risk_count"] == 2
    assert 0 <= result["avg_risk_score"] <= 1
    assert 0 <= result["avg_failure_probability"] <= 1


def test_aggregate_empty_dataframe():
    df = pd.DataFrame({"risk_status": [], "risk_score": [], "failure_probability": []})

    result = aggregate(df)

    assert result["total_structures"] == 0
    assert result["critical_risk_count"] == 0
    assert result["warning_risk_count"] == 0
    assert result["safe_risk_count"] == 0


def test_aggregate_only_one_class():
    df = pd.DataFrame(
        {
            "risk_status": ["CRITICAL", "CRITICAL", "CRITICAL"],
            "risk_score": [0.9, 0.8, 0.95],
            "failure_probability": [0.7, 0.6, 0.9],
        }
    )

    result = aggregate(df)

    assert result["total_structures"] == 3
    assert result["critical_risk_count"] == 3
    assert result["warning_risk_count"] == 0
    assert result["safe_risk_count"] == 0


def test_aggregate_missing_column():
    df = pd.DataFrame({
        "wrong_column": [1, 2, 3]
    })

    with pytest.raises(ValueError):
        aggregate(df)
