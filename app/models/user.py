"""
User model - federated via Azure AD.
"""
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    azure_object_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")