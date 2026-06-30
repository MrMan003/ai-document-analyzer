"""
Audit Log model - tracks user actions for compliance.
"""
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    action = Column(String(200), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(36), nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")