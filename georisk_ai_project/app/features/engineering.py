import pandas as pd
import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)

EPS = 1e-6
DROP_COLS = {"target", "failure", "anomaly"}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting feature engineering...")

    df = df.copy()

    feature_cols = get_feature_columns(df)
    if not feature_cols:
        raise ValueError("No feature columns found")

    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)

    df["feature_mean"] = df[feature_cols].mean(axis=1)
    df["feature_std"] = df[feature_cols].std(axis=1)
    df["feature_max"] = df[feature_cols].max(axis=1)
    df["feature_min"] = df[feature_cols].min(axis=1)

    df["strain_rate"] = df["feature_std"] / (df["feature_mean"].abs() + EPS)

    if "timestamp" in df.columns:
        df["displacement_proxy"] = df["feature_mean"].diff().abs()
    else:
        df["displacement_proxy"] = df["feature_mean"].pct_change().abs()

    df["sensor_instability"] = df["feature_max"] - df["feature_min"]
    df["pressure_index"] = df["feature_mean"] * df["feature_std"]

    window = 10 if len(df) > 10 else 3
    rolling_mean = df["feature_mean"].rolling(window, min_periods=1).mean()
    rolling_std = df["feature_mean"].rolling(window, min_periods=1).std()

    df["z_score"] = (df["feature_mean"] - rolling_mean) / (rolling_std + EPS)
    df["anomaly_score_proxy"] = df["z_score"].abs()

    df = df.replace([np.inf, -np.inf], np.nan)

    if df.isna().sum().sum() > 0:
        logger.warning("NaN detected — applying safe fill strategy")

    df = df.ffill().bfill().fillna(0)

    df = _normalize_columns(
        df,
        [
            "strain_rate",
            "displacement_proxy",
            "sensor_instability",
            "pressure_index",
            "anomaly_score_proxy",
        ],
    )

    logger.info("Feature engineering completed")
    return df


def get_feature_columns(df: pd.DataFrame):
    return [
        col
        for col in df.columns
        if col.startswith("feature_") and col not in DROP_COLS
    ]


def _normalize_columns(df: pd.DataFrame, cols: list[str]):
    for col in cols:
        q_low = df[col].quantile(0.01)
        q_high = df[col].quantile(0.99)

        if q_high - q_low == 0:
            df[col] = 0.0
        else:
            df[col] = (df[col] - q_low) / (q_high - q_low)
            df[col] = df[col].clip(0, 1)

    return df
