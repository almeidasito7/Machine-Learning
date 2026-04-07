import pandas as pd
import pytest

from app.services.pipeline.base_pipeline import BasePipeline


def test_base_pipeline_validate_rejects_none():
    pipeline = BasePipeline()
    with pytest.raises(ValueError):
        pipeline._validate(None, stage="test")


def test_base_pipeline_validate_rejects_empty_dataframe():
    pipeline = BasePipeline()
    with pytest.raises(ValueError):
        pipeline._validate(pd.DataFrame(), stage="test")


def test_base_pipeline_validate_requires_columns():
    pipeline = BasePipeline()
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        pipeline._validate(df, stage="test", required_columns=["a", "b"])
