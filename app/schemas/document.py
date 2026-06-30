"""
Document schemas for API validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    filename: str
    file_size_bytes: int


class DocumentCreate(DocumentBase):
    owner_id: str
    storage_path: str
    file_hash: str


class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    page_count: Optional[int] = None
    document_type: Optional[str] = None
    language: Optional[str] = None
    error_message: Optional[str] = None


class DocumentOut(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    status: str
    page_count: Optional[int] = None
    document_type: Optional[str] = None
    language: str
    is_scanned: bool
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DocumentListOut(BaseModel):
    items: List[DocumentOut]
    total: int
    skip: int
    limit: int


class AnalysisResult(BaseModel):
    """Full analysis result for a document."""
    model_config = ConfigDict(from_attributes=True)
    
    document: DocumentOut
    extraction: Optional["ExtractionOut"] = None
    risks: List["RiskOut"] = []
    summary: Optional["SummaryOut"] = None


# Import these at the bottom to avoid circular imports
from app.schemas.extraction import ExtractionOut
from app.schemas.risk import RiskOut
from app.schemas.summary import SummaryOut

# Update forward references
AnalysisResult.model_rebuild()