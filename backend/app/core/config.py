from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables (see docker-compose.yml)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Cloud ML Platform API"
    version: str = "0.1.0"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    # Auth — the default secret is for local dev only, always overridden in production
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Infrastructure endpoints — wired in from Sprint 2 onwards
    database_url: str = "postgresql+psycopg://mlops:mlops-dev-password@localhost:5432/mlplatform"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:29092"
    mlflow_tracking_uri: str = "http://localhost:5001"


settings = Settings()
