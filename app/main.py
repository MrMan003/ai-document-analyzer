"""
AI Document Analyzer - FastAPI application entrypoint.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging
from app.middleware import RequestIDMiddleware, LoggingMiddleware, ErrorHandlerMiddleware
from app.routers import auth, documents, analytics

# Comment out Celery for now
# from app.workers import celery_app

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")

    # Create tables if using SQLite (for production, use Alembic migrations)
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Automated RFP/tender document analysis: extraction, summarization, and risk identification.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(analytics.router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")