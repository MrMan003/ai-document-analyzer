"""
OCR service for scanned PDFs.
"""
from typing import Tuple
import tempfile
import os

from pdf2image import convert_from_path
import pytesseract


class OCRService:
    """OCR service for scanned documents."""

    def __init__(self):
        self.tesseract_cmd = os.environ.get("TESSERACT_CMD", "tesseract")

    def process(self, file_path: str, max_pages: int = 50) -> Tuple[str, int]:
        """
        Process a scanned PDF with OCR.
        Returns (extracted_text, page_count).
        """
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, first_page=1, last_page=max_pages)

            text_chunks = []
            for i, image in enumerate(images):
                # Extract text using Tesseract
                page_text = pytesseract.image_to_string(image)
                text_chunks.append(f"--- Page {i + 1} ---\n{page_text}")

            return "\n\n".join(text_chunks), len(images)

        except Exception as e:
            raise ValueError(f"OCR processing failed: {str(e)}")

    def is_scanned(self, file_path: str) -> bool:
        """Check if PDF appears to be scanned."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)

            # Check first few pages for text
            for i, page in enumerate(reader.pages):
                if i >= 3:
                    break
                text = page.extract_text() or ""
                if text.strip():
                    return False

            return True
        except Exception:
            return True

ocr_service = OCRService()