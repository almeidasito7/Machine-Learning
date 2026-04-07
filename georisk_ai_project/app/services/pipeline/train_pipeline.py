import json

from app.services.pipeline.base_pipeline import BasePipeline
from app.ingestion.loader import load_dataset
from app.features.mapping import map_to_geotechnical
from app.features.engineering import DROP_COLS, engineer_features
from app.models.anomaly import train_anomaly_detector
from app.models.predictor import train_failure_predictor
from app.core.config import settings
from app.core.logging import get_logger

from sklearn.model_selection import train_test_split

logger = get_logger(__name__)

MODEL_METADATA_PATH = settings.model_path / "model_metadata.json"


class TrainPipeline(BasePipeline):

    def run(self, retrain_model: bool = False):
        self._log_start("TRAIN PIPELINE")

        if MODEL_METADATA_PATH.exists() and not retrain_model:
            logger.info("Model already exists. Use retrain_model=True to force retraining.")
            self._log_end("TRAIN PIPELINE")
            return {"status": "model already exists"}

        df = load_dataset(dataset_type="train")
        self._validate(df, "raw")

        df = map_to_geotechnical(df)
        self._validate(df, "mapped")

        df = engineer_features(df)
        self._validate(df, "features")

        if "target" not in df.columns:
            raise ValueError("Dataset must contain 'target' column")

        y = (df["target"] > 0).astype(int)
        logger.info(f"train: target distribution={y.value_counts(normalize=True).to_dict()}")
        if y.nunique() < 2:
            if not {"strain_rate", "anomaly_score_proxy", "pressure_index"}.issubset(df.columns):
                raise ValueError("Training target must contain both classes (0 and 1)")

            proxy_score = (
                0.5 * df["anomaly_score_proxy"].astype(float)
                + 0.3 * df["strain_rate"].astype(float)
                + 0.2 * df["pressure_index"].astype(float)
            )
            threshold = float(proxy_score.quantile(0.90))
            y = (proxy_score >= threshold).astype(int)

            if y.nunique() < 2:
                raise ValueError("Training target must contain both classes (0 and 1)")

            df["target"] = y
            logger.warning(
                f"train: original target is degenerate; using proxy target distribution="
                f"{y.value_counts(normalize=True).to_dict()}"
            )

        feature_cols = sorted(
            [col for col in df.columns if col.startswith("feature_") and col not in DROP_COLS]
        )
        if not feature_cols:
            raise ValueError("No feature_* columns found")

        X = df[feature_cols]

        stratify = y if y.nunique() > 1 else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=stratify,
        )

        train_anomaly_detector(X_train)

        _, metrics = train_failure_predictor(
            X_train,
            y_train,
            X_test,
            y_test,
        )
        logger.info(f"train: failure_metrics={metrics}")

        metadata = {
            "features": feature_cols,
            "target": "target",
            "target_mode": "binary",
            "metrics": metrics,
            "failure_threshold": float(metrics.get("threshold", 0.5)),
        }

        settings.model_path.mkdir(parents=True, exist_ok=True)
        with open(MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self._log_end("TRAIN PIPELINE")

        return {
            "status": "models trained",
            "metrics": metrics,
            "feature_count": len(feature_cols),
        }


def train_pipeline(retrain_model: bool = False):
    return TrainPipeline().run(retrain_model=retrain_model)
