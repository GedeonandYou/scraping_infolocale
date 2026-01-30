"""Pydantic schemas for Event API endpoints."""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EventBase(BaseModel):
    """Base schema for Event - champs communs."""

    title: str = Field(..., max_length=500, description="Titre de l'événement")
    category: Optional[str] = Field(None, max_length=255, description="Catégorie")
    begin_date: Optional[date] = Field(None, description="Date de début")
    end_date: Optional[date] = Field(None, description="Date de fin")
    start_time: Optional[str] = Field(None, max_length=10, description="Heure de début (HH:MM)")
    end_time: Optional[str] = Field(None, max_length=10, description="Heure de fin (HH:MM)")
    description: Optional[str] = Field(None, description="Description complète")
    organizer: Optional[str] = Field(None, max_length=500, description="Organisateur")
    pricing: Optional[str] = Field(None, max_length=200, description="Tarification")
    website: Optional[str] = Field(None, max_length=500, description="Site web")
    tags: Optional[list[str]] = Field(None, description="Tags")
    artists: Optional[list[str]] = Field(None, description="Artistes/Performers")
    sponsors: Optional[list[str]] = Field(None, description="Sponsors")

    # Localisation
    location_name: Optional[str] = Field(None, max_length=500, description="Nom du lieu")
    address: Optional[str] = Field(None, max_length=500, description="Adresse")
    zipcode: Optional[str] = Field(None, max_length=20, description="Code postal")
    city: Optional[str] = Field(None, max_length=200, description="Ville")
    state: Optional[str] = Field(None, max_length=255, description="Département/Région")
    country: Optional[str] = Field(None, max_length=255, description="Pays")

    # Coordonnées GPS
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    display_name: Optional[str] = Field(None, max_length=1000, description="Adresse formatée")

    # Google Places
    place_id: Optional[str] = Field(None, max_length=255, description="Google Place ID")
    place_name: Optional[str] = Field(None, max_length=500, description="Nom du lieu (Google)")
    place_types: Optional[list[str]] = Field(None, description="Types Google Places")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Note Google Places")

    # Champs techniques
    image_path: Optional[str] = Field(None, max_length=500, description="Chemin de l'image")
    qr_code: Optional[str] = Field(None, description="Contenu du QR code")
    schema_org_types: Optional[list[str]] = Field(None, description="Types Schema.org")
    raw_json: Optional[dict] = Field(None, description="Données brutes JSON")
    is_private: bool = Field(default=False, description="Événement privé")


class EventCreate(EventBase):
    """Schema pour créer un événement."""

    uid: str = Field(..., max_length=100, description="Identifiant unique (déduplication)")
    user_id: int = Field(..., description="ID de l'utilisateur propriétaire")


class EventUpdate(BaseModel):
    """Schema pour mettre à jour un événement - tous les champs optionnels."""

    title: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=255)
    begin_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[str] = Field(None, max_length=10)
    end_time: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    organizer: Optional[str] = Field(None, max_length=500)
    pricing: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    location_name: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=200)
    is_private: Optional[bool] = None


class EventRead(EventBase):
    """Schema pour lire un événement - avec ID et timestamps."""

    id: int
    uid: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """Schema pour la réponse de liste d'événements avec pagination."""

    total: int = Field(..., description="Nombre total d'événements")
    page: int = Field(..., description="Page courante")
    page_size: int = Field(..., description="Nombre d'éléments par page")
    events: list[EventRead] = Field(..., description="Liste des événements")


class EventFilter(BaseModel):
    """Schema pour filtrer les événements."""

    category: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    begin_date_from: Optional[date] = None
    begin_date_to: Optional[date] = None
    search: Optional[str] = Field(None, description="Recherche dans titre/description")
    is_private: Optional[bool] = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
