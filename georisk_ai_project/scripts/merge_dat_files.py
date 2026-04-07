import os
import numpy as np
import pandas as pd
from glob import glob
from sklearn.datasets import load_svmlight_file

RAW_PATH = "data/raw"
OUTPUT_PATH = "data/processed/dataset_merged.csv"


def load_dat_file(path):
    try:
        X, y = load_svmlight_file(path)

        X = X.toarray()  # Convert sparse matrix to dense.

        df = pd.DataFrame(X)
        df["target"] = y

        return df

    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return None


def merge_files():
    files = glob(os.path.join(RAW_PATH, "*.dat"))

    if not files:
        raise ValueError("No .dat files found in data/raw")

    print(f"[INFO] Found {len(files)} files")

    dfs = []
    for file in files:
        df = load_dat_file(file)
        if df is not None:
            dfs.append(df)

    if not dfs:
        raise ValueError("All files failed to load")

    merged = pd.concat(dfs, ignore_index=True)

    print(f"[INFO] Merged dataset shape: {merged.shape}")

    # Rename feature columns.
    feature_cols = [f"feature_{i}" for i in range(1, merged.shape[1])]
    merged.columns = feature_cols + ["target"]

    # Basic validation.
    if merged.isna().sum().sum() > 0:
        print("[WARNING] NaN detected — filling with 0")
        merged = merged.fillna(0)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    merged.to_csv(OUTPUT_PATH, index=False)

    print(f"[SUCCESS] Dataset saved at {OUTPUT_PATH}")


if __name__ == "__main__":
    merge_files()
