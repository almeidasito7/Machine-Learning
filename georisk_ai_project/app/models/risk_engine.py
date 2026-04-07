import pandas as pd


def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = [
        "failure_probability",
        "anomaly_score_model",
        "strain_rate",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()

    df["failure_probability"] = df["failure_probability"].clip(0, 1)
    df["anomaly_score_model"] = _normalize(df["anomaly_score_model"])
    df["strain_rate"] = df["strain_rate"].clip(0, 1)

    w_failure = 0.5
    w_anomaly = 0.3
    w_strain = 0.2

    df["risk_score"] = (
        df["failure_probability"] * w_failure +
        df["anomaly_score_model"] * w_anomaly +
        df["strain_rate"] * w_strain
    ).clip(0, 1)

    df["risk_status"] = df["risk_score"].apply(_classify)

    df["risk_breakdown"] = df.apply(
        lambda row: {
            "failure": row["failure_probability"] * w_failure,
            "anomaly": row["anomaly_score_model"] * w_anomaly,
            "strain": row["strain_rate"] * w_strain,
        },
        axis=1,
    )

    return df


def _normalize(series: pd.Series):
    min_val = series.min()
    max_val = series.max()

    if max_val - min_val == 0:
        return 0

    return (series - min_val) / (max_val - min_val)


def _classify(score: float) -> str:
    if score >= 0.6:
        return "CRITICAL"
    elif score >= 0.3:
        return "WARNING"
    return "SAFE"
