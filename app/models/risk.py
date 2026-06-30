"""
Risk model - identified risks from document analysis.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.enums import RiskSeverity, RiskCategory, MitigationStatus


class Risk(BaseModel):
    __tablename__ = "risks"

    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default=RiskSeverity.MEDIUM.value, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    recommendation = Column(Text, nullable=True)
    mitigation_status = Column(String(20), default=MitigationStatus.PENDING.value, nullable=False)
    impact_score = Column(Integer, nullable=True)
    likelihood_score = Column(Integer, nullable=True)
    risk_score = Column(Integer, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="risks")