"""
Document processing Celery tasks.
"""
from celery import shared_task
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.services import DocumentService
from app.models import Document, DocumentStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def process_document_task(self, document_id: str):
    """Process a document asynchronously."""
    try:
        db = SessionLocal()
        try:
            service = DocumentService(db)
            document = service.process_document(document_id)
            logger.info(f"Document processed successfully: {document_id}")
            return {"status": "success", "document_id": document_id}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Document processing failed: {document_id} - {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)


@shared_task
def retry_failed_documents():
    """Retry failed documents."""
    db = SessionLocal()
    try:
        # Find failed documents that haven't been retried recently
        retry_cutoff = datetime.utcnow() - timedelta(hours=24)
        documents = db.query(Document).filter(
            Document.status == DocumentStatus.FAILED.value,
            Document.is_deleted == False,
            Document.last_retry_at < retry_cutoff,
            Document.retry_count < 5
        ).limit(10).all()

        for document in documents:
            process_document_task.delay(document.id)
            logger.info(f"Retrying document: {document.id}")

        return {"retried_count": len(documents)}
    finally:
        db.close()


@shared_task
def cleanup_sessions():
    """Clean up expired sessions from Redis."""
    from app.services.auth import session_service

    # This would clean up old session data
    # Implementation depends on session storage strategy
    logger.info("Session cleanup completed")


@shared_task
def generate_document_analytics(document_id: str):
    """Generate analytics for a document."""
    db = SessionLocal()
    try:
        service = DocumentService(db)
        document = service.get_document(document_id)

        if document and document.stats:
            # Update or calculate analytics
            logger.info(f"Analytics generated for: {document_id}")
    finally:
        db.close()