"""
Base model with common fields.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class BaseModel(Base):
    """Abstract base model with common fields."""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"