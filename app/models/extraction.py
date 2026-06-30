"""
Extraction model - structured data extracted from documents.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Text, DateTime, String, Float, Integer, ForeignKey
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModel

# Use JSON for SQLite, JSONB for PostgreSQL
try:
    from sqlalchemy.dialects.postgresql import JSONB
    # Check if we're using PostgreSQL
    from app.core.config import settings
    if settings.DATABASE_URL.startswith("postgresql"):
        JSONType = JSONB
    else:
        JSONType = SQLiteJSON
except:
    JSONType = SQLiteJSON


class Extraction(BaseModel):
    __tablename__ = "extractions"

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)

    # Text fields
    scope_of_work = Column(Text, nullable=True)
    timeline = Column(Text, nullable=True)
    eligibility_criteria = Column(Text, nullable=True)

    # Structured JSON fields
    timeline_json = Column(JSONType, nullable=True)
    eligibility_json = Column(JSONType, nullable=True)
    budget_info = Column(JSONType, nullable=True)
    evaluation_criteria = Column(JSONType, nullable=True)
    submission_requirements = Column(JSONType, nullable=True)
    contact_info = Column(JSONType, nullable=True)

    # Confidence scores
    confidence_scope = Column(Float, nullable=True)
    confidence_timeline = Column(Float, nullable=True)
    confidence_eligibility = Column(Float, nullable=True)

    # Processing metadata
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_used = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    raw_model_response = Column(Text, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="extraction")