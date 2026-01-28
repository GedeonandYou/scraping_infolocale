"""Database configuration and session management."""

from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import event, Index
from src.config.settings import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def create_db_and_tables():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)

    # Create indexes after table creation
    with Session(engine) as session:
        # Index sur user_id
        Index('idx_scanned_events_user', 'user_id').create(engine, checkfirst=True)

        # Index sur is_private
        Index('idx_scanned_events_private', 'is_private').create(engine, checkfirst=True)

        # Index composite sur latitude et longitude
        Index('idx_scanned_events_coords', 'latitude', 'longitude').create(engine, checkfirst=True)

        session.commit()


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
