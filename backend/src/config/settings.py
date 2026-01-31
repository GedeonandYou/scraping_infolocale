"""Application configuration using Pydantic Settings.

Chargement explicite de .env (python-dotenv) et gestion d'une URL
`DATABASE_URL` optionnelle qui prend le pas sur la construction à partir
des composants POSTGRES_*.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Charger .env le plus tôt possible pour peupler os.environ
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Composants base de données
    POSTGRES_USER: str = "infolocale_user"
    POSTGRES_PASSWORD: str = "pwd_infolocale"
    POSTGRES_DB: str = "infolocale_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # DSN complet optionnel (si défini, prioritaire)
    DATABASE_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Retourne l'URL effective de connexion à la base.

        Priorité:
        1) Si `DATABASE_URL` est défini et non vide → utilisé tel quel.
        2) Sinon, construire l'URL depuis les variables POSTGRES_*.
        """
        if self.DATABASE_URL and str(self.DATABASE_URL).strip():
            return str(self.DATABASE_URL).strip()
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

    # Export Paths
    EXPORT_CSV_PATH: str = "data/exports/events.csv"
    EXPORT_JSON_PATH: str = "data/exports/events.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
