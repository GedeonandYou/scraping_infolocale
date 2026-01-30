"""User model for authentication and event ownership."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    """User model - référence pour la table users."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    pseudo: str = Field(max_length=100, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)

    # Email confirmation
    email_confirmed: bool = Field(default=False)
    confirmation_token: Optional[str] = Field(default=None, max_length=255)
    confirmation_sent_at: Optional[datetime] = Field(default=None)

    # Password reset
    reset_token: Optional[str] = Field(default=None, max_length=255)
    reset_sent_at: Optional[datetime] = Field(default=None)

    # Device tracking
    device_id: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = Field(default=None)

    # Relationship
    # events: list["ScannedEvent"] = Relationship(back_populates="user")
