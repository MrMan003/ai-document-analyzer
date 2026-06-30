"""
Audit logging service.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.audit_repo import AuditRepository


class AuditService:
    """Audit logging service."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)

    async def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an action to the audit log."""
        self.repo.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details
        )
        self.db.commit()

    def get_user_actions(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> list:
        """Get audit logs for a user."""
        return self.repo.get_user_actions(user_id, limit, skip)

    def get_resource_actions(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> list:
        """Get audit logs for a resource."""
        return self.repo.get_resource_actions(resource_type, resource_id, limit)