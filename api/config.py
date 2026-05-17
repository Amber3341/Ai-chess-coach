from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ChessMentor AI"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./dev.db"
    upload_dir: Path = Path("uploads")
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5174,http://localhost:5174"
    stockfish_path: Path | None = None
    stockfish_depth: int = 12
    stockfish_time_limit_seconds: float = 0.1
    jwt_secret_key: str = "default_secret_for_local_dev_only_change_in_prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    gemini_api_key: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection: str = "chess-theory"
    gcp_project_id: str | None = None
    gcs_bucket_name: str | None = None
    gcp_pubsub_topic_id: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
