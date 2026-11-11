from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Quick Commerce API"
    debug: bool = False
    log_level: str = "INFO"
    request_timeout_seconds: float = 30
    max_body_bytes: int = 1_000_000  # 1 MB is plenty for JSON
    database_url: str  # no default, so the app fails at startup if it's missing
    # Frontends allowed to call the API. Set in .env as a JSON list, e.g.
    # CORS_ORIGINS='["https://shop.example.com"]'
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
