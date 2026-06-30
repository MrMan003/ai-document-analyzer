"""
Audit log repository.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog operations."""

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """Log an action."""
        return self.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details
        )

    def get_user_actions(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
        action_filter: Optional[str] = None
    ) -> List[AuditLog]:
        """Get actions for a specific user."""
        query = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.is_deleted == False
        )
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)
        return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    def get_resource_actions(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get actions for a specific resource."""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id,
            AuditLog.is_deleted == False
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()