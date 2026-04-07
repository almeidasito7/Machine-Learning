from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=(),
    )

    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    allowed_origins: str = "*"

    model_dir: Path = Path("./data/models")
    data_dir: Path = Path("./data")
    raw_data_file: str = "gas_sensor_drift.dat"

    rolling_window: int = 5
    anomaly_contamination: float = 0.03

    risk_threshold_safe: float = 0.30
    risk_threshold_warning: float = 0.60

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, v: str):
        return v or "*"

    @property
    def cors_origins(self) -> List[str]:
        if self.allowed_origins == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def model_path(self) -> Path:
        self.model_dir.mkdir(parents=True, exist_ok=True)
        return self.model_dir

    @property
    def data_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir

    def validate_environment(self):
        if self.app_env == "production" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required in production")


settings = Settings()
