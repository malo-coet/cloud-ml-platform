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

    kafka_bootstrap_servers: str = "localhost:29092"
    # Consumer group — scale out by running several replicas in this same group
    kafka_consumer_group: str = "training-service"


settings = Settings()
