import numpy as np

from app.features.engineering import engineer_features


def test_engineer_features_adds_expected_columns(sample_df):
    df = engineer_features(sample_df)

    expected = {
        "feature_mean",
        "feature_std",
        "feature_max",
        "feature_min",
        "strain_rate",
        "displacement_proxy",
        "sensor_instability",
        "pressure_index",
        "z_score",
        "anomaly_score_proxy",
    }

    assert expected.issubset(df.columns)


def test_engineer_features_normalizes_key_outputs(sample_df):
    df = engineer_features(sample_df)

    normalized_cols = [
        "strain_rate",
        "displacement_proxy",
        "sensor_instability",
        "pressure_index",
        "anomaly_score_proxy",
    ]

    for col in normalized_cols:
        assert df[col].between(0, 1).all()


def test_engineer_features_has_no_nan_or_inf(sample_df):
    df = engineer_features(sample_df)

    assert not df.isna().any().any()

    numeric = df.select_dtypes(include=["number"])
    assert np.isfinite(numeric.to_numpy()).all()
