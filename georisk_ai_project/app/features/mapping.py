import pandas as pd


def map_to_geotechnical(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    feature_cols = [col for col in df.columns if col.startswith("feature_")]

    if not feature_cols:
        raise ValueError("No feature_* columns found in dataset")

    # Optional proxy aggregations.
    try:
        df["strain_proxy"] = df[feature_cols[:32]].mean(axis=1)
        df["pressure_proxy"] = df[feature_cols[32:64]].mean(axis=1)
        df["displacement_proxy"] = df[feature_cols[64:96]].mean(axis=1)
        df["instability_proxy"] = df[feature_cols[96:]].std(axis=1)
    except Exception:
        # Fallback to safe defaults.
        df["strain_proxy"] = 0
        df["pressure_proxy"] = 0
        df["displacement_proxy"] = 0
        df["instability_proxy"] = 0

    return df
