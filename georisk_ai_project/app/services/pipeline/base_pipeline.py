from typing import List, Optional

import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


class BasePipeline:
    def run(self):
        raise NotImplementedError("Pipeline must implement run()")

    def _validate(
        self,
        df: pd.DataFrame,
        stage: str,
        required_columns: Optional[List[str]] = None,
        strict_nan: bool = False,
    ):
        if df is None:
            raise ValueError(f"{stage}: dataframe is None")

        if df.empty:
            raise ValueError(f"{stage}: dataframe is empty")

        if required_columns:
            missing = [c for c in required_columns if c not in df.columns]
            if missing:
                raise ValueError(f"{stage}: missing columns {missing}")

        if df.isna().sum().sum() > 0:
            if strict_nan:
                raise ValueError(f"{stage}: NaN values detected")
            logger.warning(f"{stage}: NaN values detected")

    def _validate_output(self, df: pd.DataFrame):
        if df.isna().sum().sum() > 0:
            raise ValueError("output: contains NaN values")

        if "failure_probability" in df.columns:
            if not ((df["failure_probability"] >= 0) & (df["failure_probability"] <= 1)).all():
                raise ValueError("output: failure_probability out of bounds")

        if "risk_score" in df.columns:
            if not ((df["risk_score"] >= 0) & (df["risk_score"] <= 1)).all():
                raise ValueError("output: risk_score out of bounds")

    def _log_start(self, name: str):
        logger.info(f"=== {name} START ===")

    def _log_end(self, name: str):
        logger.info(f"=== {name} END ===")