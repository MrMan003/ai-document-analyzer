"""
Database engine and session management.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# Determine pool class and settings based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    pool_class = NullPool
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support these parameters
    pool_size = None
    max_overflow = None
    pool_timeout = None
else:
    pool_class = QueuePool
    connect_args = {}
    pool_size = settings.DATABASE_POOL_SIZE
    max_overflow = settings.DATABASE_MAX_OVERFLOW
    pool_timeout = settings.DATABASE_POOL_TIMEOUT

# Build engine arguments
engine_kwargs = {
    "poolclass": pool_class,
    "pool_pre_ping": True,
    "connect_args": connect_args,
}

# Only add pool parameters for non-SQLite databases
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_size"] = pool_size
    engine_kwargs["max_overflow"] = max_overflow
    engine_kwargs["pool_timeout"] = pool_timeout

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()