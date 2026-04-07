from app.models.risk_engine import compute_risk_scores


class TestRiskEngine:

    def test_should_increase_risk_monotonically(self, sample_df):
        df = sample_df.copy()

        values = [0.1, 0.5, 0.9]
        repeated = (values * ((len(df) // len(values)) + 1))[: len(df)]

        df["failure_probability"] = repeated
        df["anomaly_score_model"] = 0.2
        df["strain_rate"] = 0.2

        df = compute_risk_scores(df)

        sorted_df = df.sort_values("failure_probability")

        assert sorted_df["risk_score"].is_monotonic_increasing

    def test_should_classify_risk_status(self, sample_df):
        df = sample_df.head(3).copy()

        df["failure_probability"] = [0.0, 0.5, 1.0]
        df["anomaly_score_model"] = [0.0, 0.5, 1.0]
        df["strain_rate"] = [0.0, 0.5, 1.0]

        out = compute_risk_scores(df)

        assert {"risk_score", "risk_status", "risk_breakdown"}.issubset(out.columns)
        assert out["risk_score"].between(0, 1).all()
        assert out["risk_status"].isin(["SAFE", "WARNING", "CRITICAL"]).all()
