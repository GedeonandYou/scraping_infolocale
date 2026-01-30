"""ScannedEvent model - Table principale pour les événements scrapés."""

from datetime import datetime, date
from typing import Optional, Any
from sqlalchemy import Column, ARRAY, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ScannedEvent(SQLModel, table=True):
    """
    Modèle pour les événements scrapés depuis Infolocale.
    Conforme au schéma SQL fourni dans le cahier des charges.
    """

    __tablename__ = "scanned_events"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key to users table
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE", nullable=False)

    # Unique identifier for deduplication
    uid: str = Field(max_length=100, unique=True, nullable=False, index=True)

    # ===== CHAMPS PRINCIPAUX =====
    title: str = Field(max_length=500, nullable=False)
    category: Optional[str] = Field(default=None, max_length=255)

    # Dates et heures
    begin_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    start_time: Optional[str] = Field(default=None, max_length=10)
    end_time: Optional[str] = Field(default=None, max_length=10)

    # Contenu
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    organizer: Optional[str] = Field(default=None, max_length=500)
    pricing: Optional[str] = Field(default=None, max_length=200)
    website: Optional[str] = Field(default=None, max_length=500)

    # Arrays PostgreSQL
    tags: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )
    artists: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )
    sponsors: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )

    # ===== CHAMPS DE LOCALISATION =====
    location_name: Optional[str] = Field(default=None, max_length=500)
    address: Optional[str] = Field(default=None, max_length=500)
    zipcode: Optional[str] = Field(default=None, max_length=20)
    city: Optional[str] = Field(default=None, max_length=200)
    state: Optional[str] = Field(default=None, max_length=255)
    country: Optional[str] = Field(default=None, max_length=255)

    # GPS coordinates (from geocoding)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    display_name: Optional[str] = Field(default=None, max_length=1000)

    # ===== CHAMPS GOOGLE PLACES =====
    place_id: Optional[str] = Field(default=None, max_length=255)
    place_name: Optional[str] = Field(default=None, max_length=500)
    place_types: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )
    rating: Optional[float] = Field(default=None)

    # ===== CHAMPS TECHNIQUES =====
    image_path: Optional[str] = Field(default=None, max_length=500)
    qr_code: Optional[str] = Field(default=None, sa_column=Column(Text))
    schema_org_types: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text))
    )
    raw_json: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    is_private: bool = Field(default=False, index=True)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, server_default=text("NOW()"))
    )

    # Relationship
    # user: Optional["User"] = Relationship(back_populates="events")

    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True
