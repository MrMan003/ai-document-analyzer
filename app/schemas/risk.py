from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: str
    severity: str = "MEDIUM"
    category: Optional[str] = None
    subcategory: Optional[str] = None
    recommendation: Optional[str] = None
    impact_score: Optional[int] = Field(None, ge=1, le=5)
    likelihood_score: Optional[int] = Field(None, ge=1, le=5)


class RiskCreate(RiskBase):
    document_id: str


class RiskUpdate(RiskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    mitigation_status: Optional[str] = None


class RiskOut(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    mitigation_status: str
    risk_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime