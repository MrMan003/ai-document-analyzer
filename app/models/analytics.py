"""
Analytics model - pre-aggregated statistics for documents.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DocumentStats(BaseModel):
    __tablename__ = "document_stats"

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True)
    processing_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    risk_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    critical_risk_count = Column(Integer, default=0)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="stats")