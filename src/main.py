"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routes import router
from src.models.database import create_db_and_tables
from src.config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Infolocale Scraper API...")
    create_db_and_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down Infolocale Scraper API...")


app = FastAPI(
    title="Infolocale Scraper API",
    description="API REST pour accéder aux événements scrapés depuis Infolocale.fr",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Infolocale Scraper API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
def health():
    """Detailed health check."""
    return {
        "status": "ok",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
