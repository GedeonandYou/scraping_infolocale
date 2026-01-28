"""FastAPI routes for event management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, or_
from loguru import logger

from src.models.database import get_session
from src.models.scanned_event import ScannedEvent
from src.schemas.event import (
    EventCreate,
    EventRead,
    EventUpdate,
    EventListResponse,
    EventFilter,
)

router = APIRouter(prefix="/api/v1", tags=["events"])


@router.get("/events", response_model=EventListResponse)
def get_events(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    city: Optional[str] = Query(None, description="Filtrer par ville"),
    state: Optional[str] = Query(None, description="Filtrer par département/région"),
    search: Optional[str] = Query(None, description="Recherche dans titre/description"),
    is_private: bool = Query(False, description="Inclure les événements privés"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de la page"),
    session: Session = Depends(get_session),
):
    """
    Récupérer la liste des événements avec pagination et filtres.
    """
    # Base query
    statement = select(ScannedEvent).where(ScannedEvent.is_private == is_private)

    # Apply filters
    if category:
        statement = statement.where(ScannedEvent.category == category)

    if city:
        statement = statement.where(ScannedEvent.city.ilike(f"%{city}%"))

    if state:
        statement = statement.where(ScannedEvent.state.ilike(f"%{state}%"))

    if search:
        statement = statement.where(
            or_(
                ScannedEvent.title.ilike(f"%{search}%"),
                ScannedEvent.description.ilike(f"%{search}%"),
            )
        )

    # Count total
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    # Execute query
    events = session.exec(statement).all()

    return EventListResponse(
        total=total,
        page=page,
        page_size=page_size,
        events=events,
    )


@router.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: int, session: Session = Depends(get_session)):
    """
    Récupérer un événement spécifique par son ID.
    """
    event = session.get(ScannedEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=EventRead, status_code=201)
def create_event(event: EventCreate, session: Session = Depends(get_session)):
    """
    Créer un nouvel événement.
    """
    # Check if UID already exists
    existing = session.exec(
        select(ScannedEvent).where(ScannedEvent.uid == event.uid)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Event with uid={event.uid} already exists"
        )

    db_event = ScannedEvent.model_validate(event)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    logger.info(f"Created event: {db_event.title} (id={db_event.id})")
    return db_event


@router.patch("/events/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    session: Session = Depends(get_session)
):
    """
    Mettre à jour un événement existant.
    """
    db_event = session.get(ScannedEvent, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update only provided fields
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    logger.info(f"Updated event: {db_event.title} (id={db_event.id})")
    return db_event


@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, session: Session = Depends(get_session)):
    """
    Supprimer un événement.
    """
    event = session.get(ScannedEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(event)
    session.commit()

    logger.info(f"Deleted event: {event.title} (id={event_id})")
    return None


@router.get("/categories", response_model=List[str])
def get_categories(session: Session = Depends(get_session)):
    """
    Récupérer la liste des catégories d'événements.
    """
    statement = select(ScannedEvent.category).distinct()
    categories = session.exec(statement).all()
    return [cat for cat in categories if cat]


@router.get("/cities", response_model=List[str])
def get_cities(
    state: Optional[str] = Query(None, description="Filtrer par département/région"),
    session: Session = Depends(get_session)
):
    """
    Récupérer la liste des villes.
    """
    statement = select(ScannedEvent.city).distinct()

    if state:
        statement = statement.where(ScannedEvent.state == state)

    cities = session.exec(statement).all()
    return [city for city in cities if city]


@router.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    """
    Récupérer les statistiques sur les événements.
    """
    total_events = session.exec(select(func.count(ScannedEvent.id))).one()

    events_by_category = session.exec(
        select(ScannedEvent.category, func.count(ScannedEvent.id))
        .group_by(ScannedEvent.category)
    ).all()

    events_by_city = session.exec(
        select(ScannedEvent.city, func.count(ScannedEvent.id))
        .group_by(ScannedEvent.city)
        .order_by(func.count(ScannedEvent.id).desc())
        .limit(10)
    ).all()

    return {
        "total_events": total_events,
        "events_by_category": [
            {"category": cat, "count": count}
            for cat, count in events_by_category
            if cat
        ],
        "top_10_cities": [
            {"city": city, "count": count}
            for city, count in events_by_city
            if city
        ],
    }
