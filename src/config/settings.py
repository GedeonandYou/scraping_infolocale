"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    POSTGRES_USER: str = "infolocale_user"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "infolocale_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Google Places API
    GOOGLE_PLACES_API_KEY: str = ""

    # Scraping
    SCRAPING_DELAY: int = 2
    SCRAPING_USER_AGENT: str = "InfoLocaleScraper/1.0 (Educational Project)"
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3

    # Default User ID
    DEFAULT_USER_ID: int = 1

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/scraper.log"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_PERIOD: int = 60

    # Export Paths
    EXPORT_CSV_PATH: str = "data/exports/events.csv"
    EXPORT_JSON_PATH: str = "data/exports/events.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
