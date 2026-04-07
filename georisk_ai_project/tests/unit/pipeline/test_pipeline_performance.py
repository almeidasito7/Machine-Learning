import time
from app.features.engineering import engineer_features


class TestPipelinePerformance:

    def test_should_run_under_time_limit(self, sample_df):
        start = time.perf_counter()

        engineer_features(sample_df)

        duration = time.perf_counter() - start

        assert duration < 5
