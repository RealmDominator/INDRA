"""
INDRA — Settings (Pydantic-Settings)

Loads configuration from environment variables / .env file.
All values have safe defaults for local development.
Do NOT hard-code secrets here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    # Database
    database_url: str = ""
    entity_resolution_threshold: int = 85

    # CORS — local frontend dev server
    frontend_url: str = "http://localhost:3000"

    # LLM (provider abstracted — NOT selected yet)
    llm_provider: str = "none"   # will be set when LLM step begins
    llm_model: str = "not_configured"

@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
