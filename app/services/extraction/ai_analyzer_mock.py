"""
LLM-based RFP/tender analysis - uses mock mode for testing.
"""
import json
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Import mock analyzer
from app.services.extraction.ai_analyzer_mock import analyze_document as mock_analyze


class AIAnalyzer:
    """AI analysis service using mock for testing."""

    def __init__(self):
        self.use_mock = True
        logger.info("Using MOCK AI analyzer (no API key required)")

    async def analyze(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze document text using mock.
        """
        logger.info("Using mock analyzer for document")
        # The mock_analyze is already async, so await it
        result = await mock_analyze(document_text)
        return result


ai_analyzer = AIAnalyzer()