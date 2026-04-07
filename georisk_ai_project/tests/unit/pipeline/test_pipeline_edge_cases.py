from app.features.engineering import engineer_features


class TestPipelineEdgeCases:

    def test_should_handle_extreme_values(self, sample_df):
        df = sample_df.copy()

        numeric_cols = df.select_dtypes(include=["number"]).columns
        df.loc[0, numeric_cols] = 1e9

        df = engineer_features(df)

        assert not df.isna().any().any()

    def test_should_handle_missing_values(self, sample_df):
        df = sample_df.copy()

        df.iloc[0, 0] = None

        df = engineer_features(df)

        assert not df.isna().any().any()