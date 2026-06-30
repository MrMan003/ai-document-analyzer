"""
PDF text extraction utility.
"""
from typing import Tuple
from pathlib import Path
import os

from pypdf import PdfReader


class PDFExtractor:
    """PDF text extraction service."""

    MAX_CHARS = 100_000

    def extract_text(self, file_path: str, max_chars: int = None) -> Tuple[str, int]:
        """
        Extract plain text from a PDF file.
        Returns (text, page_count).
        """
        if max_chars is None:
            max_chars = self.MAX_CHARS

        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        chunks = []
        total_len = 0

        for page in reader.pages:
            page_text = page.extract_text() or ""
            chunks.append(page_text)
            total_len += len(page_text)
            if total_len >= max_chars:
                break

        text = "\n\n".join(chunks)
        return text[:max_chars], page_count

    def has_text(self, file_path: str) -> bool:
        """Check if PDF contains extractable text."""
        try:
            text, _ = self.extract_text(file_path, max_chars=1000)
            return bool(text.strip())
        except Exception:
            return False

pdf_extractor = PDFExtractor()