import pandas as pd


def aggregate(df: pd.DataFrame) -> dict:
    if "risk_status" not in df.columns:
        raise ValueError("Missing required column: risk_status")

    total = len(df)

    critical = (df["risk_status"] == "CRITICAL").sum()
    warning = (df["risk_status"] == "WARNING").sum()
    safe = (df["risk_status"] == "SAFE").sum()

    return {
        "total_structures": int(total),
        "critical_risk_count": int(critical),
        "warning_risk_count": int(warning),
        "safe_risk_count": int(safe),
        "avg_risk_score": float(df["risk_score"].mean()),
        "avg_failure_probability": float(df["failure_probability"].mean()),
    }