"""Database configuration and session management."""

from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from src.config.settings import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def create_db_and_tables():
    """
    Create all tables in the database.

    Note: Les index sont déjà définis dans les modèles SQLModel avec le paramètre index=True
    et dans le script SQL docker/init.sql pour PostgreSQL.
    """
    SQLModel.metadata.create_all(engine)


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
