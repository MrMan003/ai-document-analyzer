from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DocumentStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    risk_count: int = 0
    high_risk_count: int = 0
    critical_risk_count: int = 0
    word_count: Optional[int] = None
    page_count: Optional[int] = None


class AnalyticsDashboard(BaseModel):
    total_documents: int
    total_risks: int
    avg_processing_time: float
    documents_by_status: dict
    risks_by_severity: dict
    documents_over_time: List[dict]