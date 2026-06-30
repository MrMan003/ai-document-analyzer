from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


class TimelineItem(BaseModel):
    milestone: str
    date: Optional[str] = None
    notes: Optional[str] = None


class EligibilityItem(BaseModel):
    criterion: str
    mandatory: bool = True
    notes: Optional[str] = None


class ExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    document_id: str
    scope_of_work: Optional[str] = None
    timeline: Optional[str] = None
    timeline_items: List[TimelineItem] = Field(default_factory=list)
    eligibility_criteria: Optional[str] = None
    eligibility_items: List[EligibilityItem] = Field(default_factory=list)
    budget_info: Optional[Any] = None
    evaluation_criteria: Optional[Any] = None
    submission_requirements: Optional[Any] = None
    confidence_scope: Optional[float] = None
    confidence_timeline: Optional[float] = None
    confidence_eligibility: Optional[float] = None
    extracted_at: datetime
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None