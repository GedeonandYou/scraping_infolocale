"""Application configuration using Pydantic Settings.

Configuration professionnelle qui force l'utilisation du fichier .env
pour toutes les données sensibles. Aucune valeur par défaut pour les secrets.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Charger .env le plus tôt possible
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _PROJECT_ROOT / ".env"

if not _ENV_FILE.exists():
    raise FileNotFoundError(
        f"❌ Fichier .env introuvable: {_ENV_FILE}\n"
        f"Créez le fichier .env à partir de .env.example:\n"
        f"  cp .env.example .env\n"
        f"Puis configurez vos variables d'environnement."
    )

load_dotenv(_ENV_FILE, override=False)


class Settings(BaseSettings):
    """Application settings - All sensitive data MUST be in .env file."""

    # ==========================================
    # DATABASE CONFIGURATION (REQUIRED)
    # ==========================================
    POSTGRES_USER: str = Field(
        ...,
        description="PostgreSQL username (REQUIRED in .env)"
    )
    POSTGRES_PASSWORD: str = Field(
        ...,
        description="PostgreSQL password (REQUIRED in .env)"
    )
    POSTGRES_DB: str = Field(
        ...,
        description="PostgreSQL database name (REQUIRED in .env)"
    )
    POSTGRES_HOST: str = Field(
        default="localhost",
        description="PostgreSQL host"
    )
    POSTGRES_PORT: int = Field(
        default=5432,
        description="PostgreSQL port"
    )
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Optional full database URL (overrides POSTGRES_* vars)"
    )

    @property
    def database_url(self) -> str:
        """Build database URL from components or use DATABASE_URL if provided."""
        if self.DATABASE_URL and str(self.DATABASE_URL).strip():
            return str(self.DATABASE_URL).strip()
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ==========================================
    # API CONFIGURATION
    # ==========================================
    API_HOST: str = Field(
        default="0.0.0.0",
        description="API host address"
    )
    API_PORT: int = Field(
        default=8000,
        description="API port"
    )
    API_RELOAD: bool = Field(
        default=True,
        description="Auto-reload on code changes (dev only)"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )

    # ==========================================
    # EXTERNAL SERVICES (REQUIRED)
    # ==========================================
    OPENROUTESERVICE_API_KEY: str = Field(
        ...,
        description="OpenRouteService API key (REQUIRED in .env)"
    )

    @validator("OPENROUTESERVICE_API_KEY")
    def validate_api_key(cls, v):
        """Validate that API key is not empty."""
        if not v or not v.strip():
            raise ValueError(
                "OPENROUTESERVICE_API_KEY is required in .env file.\n"
                "Get your free API key at: https://openrouteservice.org"
            )
        return v.strip()

    # ==========================================
    # SCRAPING CONFIGURATION
    # ==========================================
    SCRAPING_DELAY: int = Field(
        default=2,
        description="Delay between requests (seconds)"
    )
    SCRAPING_USER_AGENT: str = Field(
        default="InfoLocaleScraper/1.0 (Educational Project)",
        description="User agent for web scraping"
    )
    SCRAPING_TIMEOUT: int = Field(
        default=30,
        description="Request timeout (seconds)"
    )
    SCRAPING_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retry attempts"
    )

    # ==========================================
    # APPLICATION DEFAULTS
    # ==========================================
    DEFAULT_USER_ID: int = Field(
        default=1,
        description="Default user ID for scraped events"
    )

    # ==========================================
    # LOGGING
    # ==========================================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )
    LOG_FILE: str = Field(
        default="logs/scraper.log",
        description="Log file path"
    )

    # ==========================================
    # RATE LIMITING
    # ==========================================
    RATE_LIMIT_REQUESTS: int = Field(
        default=10,
        description="Max requests per period"
    )
    RATE_LIMIT_PERIOD: int = Field(
        default=60,
        description="Rate limit period (seconds)"
    )

    # ==========================================
    # EXPORT PATHS
    # ==========================================
    EXPORT_CSV_PATH: str = Field(
        default="data/exports/events.csv",
        description="CSV export path"
    )
    EXPORT_JSON_PATH: str = Field(
        default="data/exports/events.json",
        description="JSON export path"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Raises:
        ValidationError: If required environment variables are missing
        FileNotFoundError: If .env file doesn't exist
    """
    return Settings()
