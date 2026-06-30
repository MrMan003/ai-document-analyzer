"""
Base repository with CRUD operations.
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        **filters
    ) -> List[ModelType]:
        """Get all records with filters."""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(desc(order_column) if order_desc else order_column)

        return query.offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.flush()
        return instance

    def create_bulk(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records."""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.flush()
        return instances

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update a record."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.flush()
        return instance

    def delete(self, instance: ModelType) -> None:
        """Soft delete a record."""
        instance.soft_delete()
        self.db.flush()

    def delete_permanently(self, instance: ModelType) -> None:
        """Permanently delete a record."""
        self.db.delete(instance)
        self.db.flush()

    def count(self, **filters) -> int:
        """Count records with filters."""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def exists(self, **filters) -> bool:
        """Check if a record exists with given filters."""
        return self.count(**filters) > 0