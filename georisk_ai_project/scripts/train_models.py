from app.ingestion.loader import load_dataset
from app.features.engineering import engineer_features
from app.models.anomaly import train_anomaly_detector
from app.models.predictor import train_failure_predictor

def run_training():
    df = load_dataset()
    df = engineer_features(df)

    train_anomaly_detector(df)
    train_failure_predictor(df)

    print("Training completed successfully")

if __name__ == "__main__":
    run_training()