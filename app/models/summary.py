"""
Summary model - executive summary generated from documents.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Text, DateTime, String, ForeignKey
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

# Use JSON for SQLite
try:
    from sqlalchemy.dialects.postgresql import JSONB
    from app.core.config import settings
    if settings.DATABASE_URL.startswith("postgresql"):
        JSONType = JSONB
    else:
        JSONType = SQLiteJSON
except:
    JSONType = SQLiteJSON


class Summary(BaseModel):
    __tablename__ = "summaries"

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    executive_summary = Column(Text, nullable=False)
    key_points_json = Column(JSONType, nullable=True)
    summary_type = Column(String(20), default="EXECUTIVE", nullable=False)

    # Relationships
    document = relationship("Document", back_populates="summary")