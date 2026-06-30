"""
Document model - represents uploaded RFP/tender PDF.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import DocumentStatus, DocumentType


class Document(BaseModel):
    __tablename__ = "documents"

    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    storage_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(20), default=DocumentStatus.UPLOADED.value, nullable=False, index=True)
    page_count = Column(Integer, nullable=True)
    document_type = Column(String(50), nullable=True)
    language = Column(String(10), default="en")
    is_scanned = Column(Boolean, default=False)
    processing_version = Column(Integer, default=1)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")
    extraction = relationship("Extraction", back_populates="document", uselist=False, cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="document", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="document", uselist=False, cascade="all, delete-orphan")
    stats = relationship("DocumentStats", back_populates="document", uselist=False, cascade="all, delete-orphan")