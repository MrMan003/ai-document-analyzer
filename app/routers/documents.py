"""
Document endpoints: upload, retrieve, analyze.
"""
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User, Document
from app.schemas.document import DocumentOut, DocumentListOut, AnalysisResult
from app.schemas.extraction import ExtractionOut, TimelineItem, EligibilityItem
from app.schemas.risk import RiskOut
from app.schemas.summary import SummaryOut
from app.services import DocumentService, AuditService
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/documents", tags=["Documents"])


# ============================================
# HELPER: Get mock user for testing
# ============================================
def get_mock_user():
    """Return a mock user for testing (skip authentication)."""
    return User(
        id="test-user-123",
        azure_object_id="test-azure-oid",
        email="test@example.com",
        display_name="Test User",
        is_active=True
    )


# ============================================
# ENDPOINTS
# ============================================

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document for analysis.
    
    - Validates file is PDF
    - Saves file to storage
    - Creates document record
    - Triggers background processing
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Use mock user for testing (skip authentication)
    current_user = get_mock_user()

    try:
        content = await file.read()
        service = DocumentService(db)
        document = await service.upload_document(
            owner_id=current_user.id,
            filename=file.filename or "unknown.pdf",
            file_content=content,
            ip_address=request.client.host if request.client else None
        )

        # Process synchronously (for testing)
        try:
            await service.process_document(document.id)
        except Exception as e:
            logger.error(f"Processing error: {e}")

        return document

    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("", response_model=DocumentListOut)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List documents for the current user."""
    # Use mock user for testing
    current_user = get_mock_user()
    
    service = DocumentService(db)
    documents = service.get_user_documents(current_user.id, skip, limit)
    total = service.count_user_documents(current_user.id)

    return DocumentListOut(
        items=documents,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=AnalysisResult)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get full analysis result for a document."""
    # Use mock user for testing
    current_user = get_mock_user()
    
    service = DocumentService(db)
    document = service.get_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Log view
    try:
        audit_service = AuditService(db)
        await audit_service.log_action(
            user_id=current_user.id,
            action="VIEW_DOCUMENT",
            resource_type="Document",
            resource_id=document_id
        )
    except Exception as e:
        logger.warning(f"Audit log failed: {str(e)}")

    # Build response
    extraction_out = None
    if document.extraction:
        try:
            extraction_out = ExtractionOut(
                document_id=document.id,
                scope_of_work=document.extraction.scope_of_work,
                timeline=document.extraction.timeline,
                timeline_items=json.loads(document.extraction.timeline_json) if document.extraction.timeline_json else [],
                eligibility_criteria=document.extraction.eligibility_criteria,
                eligibility_items=json.loads(document.extraction.eligibility_json) if document.extraction.eligibility_json else [],
                budget_info=document.extraction.budget_info,
                evaluation_criteria=document.extraction.evaluation_criteria,
                submission_requirements=document.extraction.submission_requirements,
                confidence_scope=document.extraction.confidence_scope,
                confidence_timeline=document.extraction.confidence_timeline,
                confidence_eligibility=document.extraction.confidence_eligibility,
                extracted_at=document.extraction.extracted_at,
                model_used=document.extraction.model_used,
                processing_time_ms=document.extraction.processing_time_ms,
                tokens_used=document.extraction.tokens_used
            )
        except Exception as e:
            logger.error(f"Error building extraction: {str(e)}")

    summary_out = None
    if document.summary:
        try:
            summary_out = SummaryOut(
                document_id=document.id,
                executive_summary=document.summary.executive_summary,
                key_points=json.loads(document.summary.key_points_json) if document.summary.key_points_json else [],
                summary_type=document.summary.summary_type,
                created_at=document.summary.created_at,
                updated_at=document.summary.updated_at
            )
        except Exception as e:
            logger.error(f"Error building summary: {str(e)}")

    # Build risks list safely
    risks = []
    for r in document.risks:
        try:
            risks.append(RiskOut.model_validate(r))
        except Exception as e:
            logger.error(f"Error validating risk: {str(e)}")

    return AnalysisResult(
        document=DocumentOut.model_validate(document),
        extraction=extraction_out,
        risks=risks,
        summary=summary_out
    )


@router.post("/{document_id}/reprocess", response_model=DocumentOut)
async def reprocess_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Re-run analysis on a document."""
    # Use mock user for testing
    current_user = get_mock_user()
    
    service = DocumentService(db)
    document = service.get_document(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        document = await service.reprocess_document(document_id)

        audit_service = AuditService(db)
        await audit_service.log_action(
            user_id=current_user.id,
            action="REPROCESS_DOCUMENT",
            resource_type="Document",
            resource_id=document_id
        )

        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document and all associated data."""
    # Use mock user for testing
    current_user = get_mock_user()
    
    service = DocumentService(db)

    if not await service.delete_document(document_id, current_user.id):
        raise HTTPException(status_code=404, detail="Document not found")

    return None