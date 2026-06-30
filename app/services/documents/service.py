"""
Document service - CRUD and processing orchestration.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models import Document, User, DocumentStatus
from app.repositories import DocumentRepository
from app.services.documents.storage import storage_service
from app.services.extraction.service import ExtractionService
from app.services.audit.service import AuditService
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Document management service."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)
        self.extraction_service = ExtractionService(db)
        self.audit_service = AuditService(db)

    async def upload_document(
        self,
        owner_id: str,
        filename: str,
        file_content: bytes,
        ip_address: Optional[str] = None
    ) -> Document:
        """Upload a new document."""
        # Check file size
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_content) > max_size:
            raise ValueError(f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB")

        # Check for duplicate (by hash)
        file_hash = storage_service.get_file_hash(file_content)
        existing = self.repo.get_by_file_hash(file_hash)
        if existing:
            raise ValueError(f"File already exists: {existing.filename}")

        # Save file
        storage_path, size = storage_service.save_file(file_content, filename)

        # Create document record
        document = self.repo.create(
            owner_id=owner_id,
            filename=filename,
            storage_path=storage_path,
            file_size_bytes=size,
            file_hash=file_hash,
            status=DocumentStatus.UPLOADED.value
        )

        # Log action
        await self.audit_service.log_action(
            user_id=owner_id,
            action="UPLOAD_DOCUMENT",
            resource_type="Document",
            resource_id=document.id,
            ip_address=ip_address,
            details={"filename": filename, "size": size}
        )

        logger.info(f"Document uploaded: {document.id} - {filename}")
        return document

    async def process_document(self, document_id: str) -> Document:
        """Process a document (extract, summarize, identify risks)."""
        document = self.repo.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            # Update status
            document = self.repo.update_status(document_id, DocumentStatus.PROCESSING.value)

            # Process with extraction service
            result = await self.extraction_service.process_document(document_id)

            # Update document
            document = self.repo.update(
                document,
                status=DocumentStatus.EXTRACTED.value,
                processed_at=datetime.utcnow(),
                page_count=result.get("page_count"),
                is_scanned=result.get("is_scanned", False)
            )

            logger.info(f"Document processed: {document_id}")
            return document

        except Exception as e:
            logger.error(f"Document processing failed: {document_id} - {str(e)}")
            document = self.repo.update_status(
                document_id,
                DocumentStatus.FAILED.value,
                error_message=str(e)
            )
            raise

    async def reprocess_document(self, document_id: str) -> Document:
        """Reprocess a failed document."""
        document = self.repo.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Increment retry count
        document = self.repo.update(
            document,
            retry_count=document.retry_count + 1,
            last_retry_at=datetime.utcnow()
        )

        return await self.process_document(document_id)

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and its associated data."""
        document = self.repo.get(document_id)
        if not document:
            return False

        # Delete physical file
        storage_service.delete_file(document.storage_path)

        # Soft delete document (cascade will handle relations)
        self.repo.delete(document)

        # Log action
        await self.audit_service.log_action(
            user_id=user_id,
            action="DELETE_DOCUMENT",
            resource_type="Document",
            resource_id=document_id
        )

        logger.info(f"Document deleted: {document_id}")
        return True

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        return self.repo.get_with_relations(document_id)

    def get_user_documents(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents for a user."""
        return self.repo.get_by_owner(user_id, skip, limit)

    def count_user_documents(self, user_id: str) -> int:
        """Count documents for a user."""
        return self.repo.count(owner_id=user_id)