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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
