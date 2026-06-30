"""
Analytics endpoints.
"""
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User, Document, Risk
from app.schemas import AnalyticsDashboard
from app.services import DocumentService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard data for the current user."""
    service = DocumentService(db)

    # Get user's documents
    documents = service.get_user_documents(current_user.id, limit=1000)

    # Calculate stats
    total_documents = len(documents)

    # Documents by status
    documents_by_status = {}
    for doc in documents:
        status = doc.status
        documents_by_status[status] = documents_by_status.get(status, 0) + 1

    # Risks by severity
    risks_by_severity = {}
    total_risks = 0
    for doc in documents:
        for risk in doc.risks:
            severity = risk.severity
            risks_by_severity[severity] = risks_by_severity.get(severity, 0) + 1
            total_risks += 1

    # Average processing time
    processing_times = [
        doc.stats.processing_time_ms
        for doc in documents
        if doc.stats and doc.stats.processing_time_ms
    ]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

    # Documents over time (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    docs_over_time = {}
    for doc in documents:
        if doc.created_at >= thirty_days_ago:
            date_key = doc.created_at.strftime("%Y-%m-%d")
            docs_over_time[date_key] = docs_over_time.get(date_key, 0) + 1

    documents_over_time = [
        {"date": date, "count": count}
        for date, count in sorted(docs_over_time.items())
    ]

    return AnalyticsDashboard(
        total_documents=total_documents,
        total_risks=total_risks,
        avg_processing_time=avg_processing_time / 1000 if avg_processing_time else 0,
        documents_by_status=documents_by_status,
        risks_by_severity=risks_by_severity,
        documents_over_time=documents_over_time[-30:]  # Last 30 days
    )


@router.get("/documents/stats")
async def get_document_stats(
    document_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stats for a specific document."""
    service = DocumentService(db)
    document = service.get_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if document.stats:
        return {
            "document_id": document.id,
            "processing_time_ms": document.stats.processing_time_ms,
            "tokens_used": document.stats.tokens_used,
            "risk_count": document.stats.risk_count,
            "high_risk_count": document.stats.high_risk_count,
            "critical_risk_count": document.stats.critical_risk_count,
            "word_count": document.stats.word_count,
            "page_count": document.stats.page_count
        }

    return {"message": "No stats available for this document"}