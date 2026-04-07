import json
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.features.engineering import DROP_COLS, engineer_features
from app.features.mapping import map_to_geotechnical
from app.ingestion.loader import load_dataset
from app.models.anomaly import detect_anomalies
from app.models.predictor import predict_failure_probability
from app.models.risk_engine import compute_risk_scores
from app.services.evaluation.evaluation_service import (
    evaluate_anomaly,
    evaluate_failure,
    evaluate_risk,
)
from app.services.openai_service import generate_narrative

logger = get_logger(__name__)

MODEL_METADATA_PATH = settings.model_path / "model_metadata.json"


def load_metadata():
    if not MODEL_METADATA_PATH.exists():
        raise FileNotFoundError("model metadata not found. run training first")

    with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def inference_pipeline(
    generate_narrative_flag: bool = True,
    dataset_type: str = "external",
    max_structures: int | None = None,
    include_raw_data: bool = False,
):
    logger.info("=== ANALYZE PIPELINE START ===")

    df = load_dataset(dataset_type=dataset_type)
    df = map_to_geotechnical(df)
    df = engineer_features(df)

    metadata = load_metadata()
    feature_cols = metadata.get("features", [])
    feature_cols = [c for c in feature_cols if c not in DROP_COLS]
    failure_threshold = float(metadata.get("failure_threshold", 0.5))

    if not feature_cols:
        raise ValueError("No features found in model metadata")

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    if "target" not in df.columns:
        raise ValueError("Dataset must contain target")

    if "structure_id" not in df.columns:
        if "batch" in df.columns:
            df["structure_id"] = df["batch"]
        else:
            df["structure_id"] = 0

    X = df[feature_cols]

    y_target = (df["target"] > 0).astype(int)
    y_failure = (df["failure"] > 0).astype(int) if "failure" in df.columns else y_target
    y_anomaly = (df["anomaly"] > 0).astype(int) if "anomaly" in df.columns else y_target
    logger.info(
        f"analyze: target={y_target.value_counts(normalize=True).to_dict()}, "
        f"failure={y_failure.value_counts(normalize=True).to_dict()}, "
        f"anomaly={y_anomaly.value_counts(normalize=True).to_dict()}"
    )

    anomaly_preds, anomaly_scores = detect_anomalies(X)
    failure_probs = predict_failure_probability(X)

    df["anomaly_score_model"] = np.asarray(anomaly_scores, dtype=float)
    desired_anomaly_rate = float(settings.anomaly_contamination)
    desired_anomaly_rate = min(max(desired_anomaly_rate, 0.0), 0.2)
    if len(df) and desired_anomaly_rate > 0:
        anomaly_threshold = float(np.quantile(df["anomaly_score_model"], 1 - desired_anomaly_rate))
        df["anomaly_pred"] = (df["anomaly_score_model"] >= anomaly_threshold).astype(int)
    else:
        df["anomaly_pred"] = (anomaly_preds == -1).astype(int)

    df["failure_probability"] = failure_probs.clip(0, 1)
    df["failure_pred"] = (df["failure_probability"] >= failure_threshold).astype(int)
    logger.info(
        f"analyze: failure_prob(mean/min/max)={float(df['failure_probability'].mean()):.4f}/"
        f"{float(df['failure_probability'].min()):.4f}/{float(df['failure_probability'].max()):.4f}, "
        f"failure_pred_rate={float(df['failure_pred'].mean()):.4f}, "
        f"anomaly_pred_rate={float(df['anomaly_pred'].mean()):.4f}"
    )

    df = compute_risk_scores(df)

    anomaly_metrics = evaluate_anomaly(y_anomaly, df["anomaly_pred"])
    failure_metrics = evaluate_failure(y_failure, df["failure_probability"], threshold=failure_threshold)
    logger.info(
        f"analyze: failure_metrics(roc_auc/f1)={failure_metrics.get('roc_auc')}/{failure_metrics.get('f1_score')}, "
        f"cm={failure_metrics.get('confusion_matrix')}"
    )

    risk_metrics = evaluate_risk(y_target, df["risk_score"])

    structures = []

    for structure_id, group in df.groupby("structure_id"):
        try:
            if structure_id is None:
                structure_id_out = None
            elif isinstance(structure_id, float):
                if structure_id == structure_id and structure_id.is_integer():
                    structure_id_out = int(structure_id)
                else:
                    structure_id_out = str(structure_id)
            elif isinstance(structure_id, (int,)):
                structure_id_out = int(structure_id)
            else:
                structure_id_out = str(structure_id)
        except Exception:
            structure_id_out = str(structure_id)

        avg_risk = float(group["risk_score"].mean())
        avg_failure = float(group["failure_probability"].mean())

        structures.append(
            {
                "structure_id": structure_id_out,
                "records": int(len(group)),
                "avg_risk_score": round(avg_risk, 4),
                "failure_probability": round(avg_failure, 4),
                "risk_level": "low",
            }
        )

    structures = sorted(structures, key=lambda x: x["avg_risk_score"], reverse=True)

    if max_structures:
        structures = structures[:max_structures]

    if len(structures) >= 10:
        scores = np.array([s["avg_risk_score"] for s in structures], dtype=float)
        high_thr = float(np.quantile(scores, 0.90))
        med_thr = float(np.quantile(scores, 0.70))
    else:
        high_thr = float(settings.risk_threshold_warning)
        med_thr = float(settings.risk_threshold_safe)

    for s in structures:
        score = float(s["avg_risk_score"])
        if score >= high_thr:
            s["risk_level"] = "high"
        elif score >= med_thr:
            s["risk_level"] = "medium"
        else:
            s["risk_level"] = "low"

    total_structures = len(structures)
    high_risk = sum(1 for s in structures if s["risk_level"] == "high")
    medium_risk = sum(1 for s in structures if s["risk_level"] == "medium")
    low_risk = sum(1 for s in structures if s["risk_level"] == "low")

    insight = None
    if generate_narrative_flag:
        insight = generate_narrative(
            {
                "total_structures": total_structures,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "avg_risk_score": round(float(df["risk_score"].mean()), 4),
                "avg_failure_probability": round(float(df["failure_probability"].mean()), 4),
                "top_structures": structures[:3],
            }
        )

    result = {
        "structures": structures,
        "total_structures": total_structures,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "thresholds": {
            "failure": failure_threshold,
            "risk_high": high_thr,
            "risk_medium": med_thr,
            "anomaly_rate_target": desired_anomaly_rate,
        },
        "kpis": {
            "anomaly": anomaly_metrics,
            "failure": failure_metrics,
            "risk": risk_metrics,
        },
        "summary": {
            "records": int(len(df)),
            "positive_target_count": int(y_target.sum()),
            "anomaly_count": int(df["anomaly_pred"].sum()),
        },
        "insight": insight,
    }

    if include_raw_data:
        result["raw_preview"] = df.head(20).to_dict(orient="records")

    logger.info("=== ANALYZE PIPELINE END ===")
    return result
