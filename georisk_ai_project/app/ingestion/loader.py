import pandas as pd

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def load_dataset(dataset_type: str = "train") -> pd.DataFrame:
    logger.info(f"Loading dataset type: {dataset_type}")

    if dataset_type == "train":
        file_path = settings.data_path / "train" / "dataset_merged.csv"
    elif dataset_type == "external":
        file_path = settings.data_path / "external" / "dataset_external.csv"
    else:
        raise ValueError(f"Invalid dataset_type: {dataset_type}")

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("Loaded dataset is empty")

    logger.info(f"Dataset loaded from {file_path}")
    logger.info(f"Shape: {df.shape}")

    return df