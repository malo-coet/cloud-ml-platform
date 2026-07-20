from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker settings, loaded from environment variables (see docker-compose.yml)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://mlops:mlops-dev-password@localhost:5432/mlplatform"
    mlflow_tracking_uri: str = "http://localhost:5001"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_datasets_bucket: str = "datasets"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"

    # Polling is a Sprint 4 stopgap — replaced by a Kafka consumer in Sprint 5
    poll_interval_seconds: float = 3.0


settings = Settings()
