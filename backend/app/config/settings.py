"""
INDRA — Settings (Pydantic-Settings)

Loads configuration from environment variables / .env file.
All values have safe defaults for local development.
Do NOT hard-code secrets here.
"""
from functools import lru_cache

from pydantic import field_validator
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

    # LLM provider configuration
    llm_provider: str = "openrouter"
    llm_model: str = "openai/gpt-4o-mini"
    openrouter_api_key: str = ""
    llm_timeout_seconds: int = 15
    llm_max_retries: int = 2

    # Ingestion — credentials (never commit)
    eia_api_key: str = ""
    acled_api_key: str = ""
    acled_email: str = ""

    # Ingestion — control
    ingestion_enabled: bool = False
    ingestion_timeout_seconds: float = 30.0
    ingestion_max_retries: int = 2
    ingestion_retry_backoff_seconds: float = 1.0

    # Ingestion — polling intervals
    ingestion_gdelt_interval_minutes: int = 15
    ingestion_rss_interval_minutes: int = 60
    ingestion_acled_interval_hours: int = 24
    ingestion_eia_interval_hours: int = 24
    ingestion_rbi_interval_hours: int = 24
    ingestion_ofac_interval_hours: int = 24

    # Ingestion — freshness thresholds
    ingestion_gdelt_stale_minutes: int = 30
    ingestion_rss_stale_minutes: int = 120
    ingestion_acled_stale_hours: int = 168
    ingestion_eia_stale_hours: int = 48
    ingestion_rbi_stale_hours: int = 72
    ingestion_ofac_stale_hours: int = 48

    # GDELT / RSS
    gdelt_query: str = ""
    gdelt_max_records: int = 25
    eia_max_records: int = 30
    acled_max_records: int = 50
    rss_feed_urls: list[str] = []

    @field_validator("rss_feed_urls", mode="before")
    @classmethod
    def parse_rss_feeds(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value or []


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
