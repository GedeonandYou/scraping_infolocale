"""Service for storing scraped events in PostgreSQL database."""

from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy.dialects.postgresql import insert
from loguru import logger

from src.models.scanned_event import ScannedEvent
from src.models.database import engine


class StorageService:
    """Service to handle database operations for scraped events."""

    def __init__(self):
        """Initialize storage service."""
        self.session = None

    def save_event(self, event_data: Dict[str, Any]) -> Optional[ScannedEvent]:
        """
        Save a single event to the database with deduplication.

        Args:
            event_data: Event data dictionary

        Returns:
            Created or existing ScannedEvent instance
        """
        try:
            with Session(engine) as session:
                # Check if event already exists by uid
                existing_event = session.exec(
                    select(ScannedEvent).where(ScannedEvent.uid == event_data['uid'])
                ).first()

                if existing_event:
                    logger.info(f"Event with uid={event_data['uid']} already exists, skipping")
                    return existing_event

                # Create new event
                event = ScannedEvent(**event_data)
                session.add(event)
                session.commit()
                session.refresh(event)

                logger.info(f"Successfully saved event: {event.title} (uid={event.uid})")
                return event

        except Exception as e:
            logger.error(f"Error saving event: {e}")
            return None

    def save_events_batch(self, events_data: List[Dict[str, Any]]) -> int:
        """
        Save multiple events in batch with deduplication using PostgreSQL UPSERT.

        Args:
            events_data: List of event data dictionaries

        Returns:
            Number of events successfully saved
        """
        if not events_data:
            return 0

        saved_count = 0

        try:
            with Session(engine) as session:
                for event_data in events_data:
                    try:
                        # Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING for deduplication
                        stmt = insert(ScannedEvent).values(**event_data)
                        stmt = stmt.on_conflict_do_nothing(index_elements=['uid'])

                        result = session.exec(stmt)

                        if result.rowcount > 0:
                            saved_count += 1
                            logger.debug(f"Inserted event with uid={event_data.get('uid')}")
                        else:
                            logger.debug(f"Event with uid={event_data.get('uid')} already exists")

                    except Exception as e:
                        logger.error(f"Error inserting event {event_data.get('uid')}: {e}")
                        continue

                session.commit()
                logger.info(f"Batch save completed: {saved_count}/{len(events_data)} events saved")

        except Exception as e:
            logger.error(f"Error in batch save: {e}")

        return saved_count

    def get_event_by_uid(self, uid: str) -> Optional[ScannedEvent]:
        """
        Get an event by its unique identifier.

        Args:
            uid: Unique identifier

        Returns:
            ScannedEvent instance or None
        """
        try:
            with Session(engine) as session:
                event = session.exec(
                    select(ScannedEvent).where(ScannedEvent.uid == uid)
                ).first()
                return event
        except Exception as e:
            logger.error(f"Error fetching event by uid={uid}: {e}")
            return None

    def get_all_uids(self) -> set[str]:
        """
        Get all existing event UIDs for deduplication checks.

        Returns:
            Set of UIDs
        """
        try:
            with Session(engine) as session:
                statement = select(ScannedEvent.uid)
                results = session.exec(statement).all()
                return set(results)
        except Exception as e:
            logger.error(f"Error fetching all UIDs: {e}")
            return set()

    def count_events(self) -> int:
        """
        Count total number of events in database.

        Returns:
            Number of events
        """
        try:
            with Session(engine) as session:
                statement = select(ScannedEvent)
                results = session.exec(statement).all()
                return len(results)
        except Exception as e:
            logger.error(f"Error counting events: {e}")
            return 0
