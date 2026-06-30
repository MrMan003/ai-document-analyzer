"""
Document repository.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document operations."""

    def __init__(self, db: Session):
        super().__init__(Document, db)

    def get_with_relations(self, document_id: str) -> Optional[Document]:
        """Get document with all related data."""
        return self.db.query(Document).options(
            selectinload(Document.extraction),
            selectinload(Document.risks),
            selectinload(Document.summary),
            selectinload(Document.stats)
        ).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

    def get_by_owner(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Document]:
        """Get documents by owner."""
        query = self.db.query(Document).filter(
            Document.owner_id == owner_id,
            Document.is_deleted == False
        )
        if status:
            query = query.filter(Document.status == status)
        return query.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()

    def get_by_status(self, status: str, limit: int = 100) -> List[Document]:
        """Get documents by status (for background processing)."""
        return self.db.query(Document).filter(
            Document.status == status,
            Document.is_deleted == False
        ).order_by(Document.uploaded_at).limit(limit).all()

    def update_status(self, document_id: str, status: str, error_message: Optional[str] = None) -> Optional[Document]:
        """Update document status."""
        document = self.get(document_id)
        if document:
            document.status = status
            if error_message is not None:
                document.error_message = error_message
            if status == "EXTRACTED":
                document.processed_at = datetime.utcnow()
            self.db.flush()
        return document

    def get_by_file_hash(self, file_hash: str) -> Optional[Document]:
        """Find document by file hash (for deduplication)."""
        return self.db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.is_deleted == False
        ).first()