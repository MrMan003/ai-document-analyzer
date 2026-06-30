"""
Extraction service - orchestrates the extraction pipeline.
"""
from typing import Dict, Any
from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.models import Document, Extraction, Risk, Summary, DocumentStats
from app.repositories import DocumentRepository
from app.services.extraction.pdf_extractor import pdf_extractor
from app.services.extraction.ai_analyzer import ai_analyzer
from app.services.extraction.ocr import ocr_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExtractionService:
    """Orchestrates document extraction, summarization, and risk identification."""

    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)

    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """Process a document through the full extraction pipeline."""
        document = self.doc_repo.get(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            logger.info(f"Starting extraction for document: {document_id}")
            
            # Extract text from PDF
            text, page_count = pdf_extractor.extract_text(document.storage_path)
            logger.info(f"Extracted {len(text)} characters from {page_count} pages")

            # Check if text was extracted (if not, try OCR)
            is_scanned = False
            if not text.strip():
                logger.info(f"No text found, attempting OCR: {document_id}")
                text, page_count = ocr_service.process(document.storage_path)
                is_scanned = True
                logger.info(f"OCR extracted {len(text)} characters from {page_count} pages")

            if not text.strip():
                raise ValueError("No extractable text found in PDF")

            # Analyze with AI
            start_time = datetime.utcnow()
            result = await ai_analyzer.analyze(text)
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"AI analysis completed in {processing_time:.2f}ms")

            # Persist results
            await self._persist_extraction(document, result, processing_time, page_count, is_scanned)

            logger.info(f"Extraction completed successfully for: {document_id}")
            
            return {
                "document_id": document_id,
                "page_count": page_count,
                "is_scanned": is_scanned,
                "processing_time_ms": processing_time,
                "tokens_used": result.get("_tokens_used", 0),
                "result": result
            }

        except Exception as e:
            logger.error(f"Extraction failed for {document_id}: {str(e)}")
            raise

    async def _persist_extraction(
        self,
        document: Document,
        result: Dict[str, Any],
        processing_time: int,
        page_count: int,
        is_scanned: bool
    ) -> None:
        """Persist all extraction results to the database."""
        try:
            # Create extraction record
            extraction = Extraction(
                document_id=document.id,
                scope_of_work=result.get("scope_of_work"),
                timeline=self._format_timeline(result.get("timeline", [])),
                timeline_json=json.dumps(result.get("timeline", [])),
                eligibility_criteria=self._format_eligibility(result.get("eligibility_criteria", [])),
                eligibility_json=json.dumps(result.get("eligibility_criteria", [])),
                model_used=result.get("_model"),
                tokens_used=result.get("_tokens_used"),
                processing_time_ms=processing_time,
                raw_model_response=result.get("_raw_response"),
                extracted_at=datetime.utcnow()
            )
            self.db.add(extraction)

            # Create summary
            summary = Summary(
                document_id=document.id,
                executive_summary=result.get("executive_summary", "No summary available"),
                key_points_json=json.dumps(result.get("key_points", [])),
                summary_type="EXECUTIVE"
            )
            self.db.add(summary)

            # Create risks
            risk_count = 0
            high_risk_count = 0
            critical_risk_count = 0

            for risk_item in result.get("risks", []):
                severity = risk_item.get("severity", "MEDIUM").upper()
                risk = Risk(
                    document_id=document.id,
                    title=risk_item.get("title", "Untitled risk")[:500],
                    description=risk_item.get("description", ""),
                    severity=severity,
                    category=risk_item.get("category", "Other"),
                    recommendation=risk_item.get("recommendation"),
                    impact_score=risk_item.get("impact_score", 3),
                    likelihood_score=risk_item.get("likelihood_score", 3),
                    risk_score=risk_item.get("risk_score", 9)
                )
                self.db.add(risk)
                risk_count += 1
                if severity == "HIGH":
                    high_risk_count += 1
                elif severity == "CRITICAL":
                    critical_risk_count += 1

            # Create stats
            stats = DocumentStats(
                document_id=document.id,
                processing_time_ms=processing_time,
                tokens_used=result.get("_tokens_used"),
                risk_count=risk_count,
                high_risk_count=high_risk_count,
                critical_risk_count=critical_risk_count,
                word_count=len(result.get("executive_summary", "").split()),
                page_count=page_count
            )
            self.db.add(stats)

            self.db.commit()
            logger.info(f"Successfully persisted extraction results for: {document.id}")

        except Exception as e:
            logger.error(f"Failed to persist extraction results: {str(e)}")
            self.db.rollback()
            raise

    def _format_timeline(self, timeline_items: list) -> str:
        """Format timeline items as readable text."""
        if not timeline_items:
            return "No timeline information available"
        
        lines = []
        for item in timeline_items:
            milestone = item.get('milestone', 'Unknown milestone')
            date = item.get('date', 'Date TBD')
            notes = item.get('notes', '')
            line = f"- {milestone} ({date})"
            if notes:
                line += f" - {notes}"
            lines.append(line)
        return "\n".join(lines)

    def _format_eligibility(self, eligibility_items: list) -> str:
        """Format eligibility items as readable text."""
        if not eligibility_items:
            return "No eligibility criteria found"
        
        lines = []
        for item in eligibility_items:
            criterion = item.get('criterion', 'Unknown criterion')
            mandatory = item.get('mandatory', True)
            notes = item.get('notes', '')
            tag = "Mandatory" if mandatory else "Optional"
            line = f"- [{tag}] {criterion}"
            if notes:
                line += f" - {notes}"
            lines.append(line)
        return "\n".join(lines)