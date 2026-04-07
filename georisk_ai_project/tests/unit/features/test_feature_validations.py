from app.features.engineering import engineer_features


class TestFeatureValidations:

    def test_should_generate_features_in_valid_range(self, sample_df):
        df = engineer_features(sample_df)

        cols = [
            "strain_rate",
            "displacement_proxy",
            "sensor_instability",
            "pressure_index",
            "anomaly_score_proxy",
        ]

        for col in cols:
            assert df[col].between(0, 1).all()
