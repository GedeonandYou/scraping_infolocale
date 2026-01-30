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

    # OpenRouteService API (Geocoding)
    OPENROUTESERVICE_API_KEY: str = ""

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

    # Geocoding batch + cache
    GEOCODING_BATCH_SIZE: int = 10
    GEOCODING_BATCH_DELAY: float = 15.0
    GEOCODING_CACHE_ENABLED: bool = True
    GEOCODING_CACHE_TTL: int = 60 * 60 * 24 * 30  # 30 days
    GEOCODING_CACHE_NEGATIVE_TTL: int = 60 * 60 * 24  # 1 day

    # Redis (Geocoding cache)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""

    @property
    def redis_url(self) -> str:
        """Build Redis URL when REDIS_URL is not explicitly provided."""
        if self.REDIS_URL:
            return self.REDIS_URL
        password = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Scraping (parallelism + region)
    SCRAPING_PARALLEL_PAGES: bool = False
    SCRAPING_MAX_WORKERS: int = 2
    SCRAPING_REGION_URL_TEMPLATE: str = "{base_url}/{region}"

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
