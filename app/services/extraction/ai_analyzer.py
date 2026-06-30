"""
LLM-based RFP/tender analysis - uses mock mode for testing.
"""
import json
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIAnalyzer:
    """AI analysis service using mock for testing."""

    def __init__(self):
        self.use_mock = True
        logger.info("Using MOCK AI analyzer (no API key required)")

    async def analyze(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze document text using mock data.
        """
        logger.info("Using mock analyzer for document")
        
        # Return mock data directly without importing external mock
        lines = document_text.split('\n')
        first_line = lines[0] if lines else "Sample RFP"
        
        return {
            "scope_of_work": f"This is a mock analysis of: {first_line[:100]}. The scope includes project management, development, and implementation services.",
            "timeline": [
                {"milestone": "Project Kickoff", "date": "2026-07-01", "notes": "Initial meeting"},
                {"milestone": "Requirements Gathering", "date": "2026-07-15", "notes": "Collect all requirements"},
                {"milestone": "Development Phase 1", "date": "2026-08-15", "notes": "First milestone delivery"},
                {"milestone": "Testing Phase", "date": "2026-09-01", "notes": "Quality assurance"},
                {"milestone": "Final Delivery", "date": "2026-09-30", "notes": "Project completion"}
            ],
            "eligibility_criteria": [
                {"criterion": "Minimum 5 years of relevant experience", "mandatory": True, "notes": "Must provide references"},
                {"criterion": "ISO 9001 certification", "mandatory": True, "notes": "Quality management"},
                {"criterion": "Local presence in the region", "mandatory": False, "notes": "Preferred but not required"},
                {"criterion": "Team size of at least 10", "mandatory": True, "notes": "Adequate resources"},
                {"criterion": "Previous government projects", "mandatory": False, "notes": "Adds weight to proposal"}
            ],
            "executive_summary": f"This RFP seeks a qualified vendor to deliver a comprehensive solution. The project requires strong technical expertise and proven track record. Key considerations include timeline, budget, and team capabilities. The selected vendor will work closely with stakeholders.",
            "key_points": [
                "Project requires experienced team",
                "Strict timeline of 3 months",
                "Budget is fixed",
                "Quality assurance is critical",
                "Vendor must provide references"
            ],
            "risks": [
                {
                    "title": "Tight Timeline",
                    "description": "The 3-month timeline is aggressive and may impact quality",
                    "severity": "HIGH",
                    "category": "Schedule",
                    "recommendation": "Negotiate for extended timeline or add more resources"
                },
                {
                    "title": "Budget Constraints",
                    "description": "Fixed budget may not cover all requirements",
                    "severity": "MEDIUM",
                    "category": "Financial",
                    "recommendation": "Clearly define scope and get sign-off on deliverables"
                },
                {
                    "title": "Resource Availability",
                    "description": "Required skills may not be readily available",
                    "severity": "MEDIUM",
                    "category": "Operational",
                    "recommendation": "Start recruitment process early, consider subcontracting"
                },
                {
                    "title": "Scope Creep",
                    "description": "Requirements may expand during the project",
                    "severity": "HIGH",
                    "category": "Technical",
                    "recommendation": "Implement strict change control process"
                },
                {
                    "title": "Compliance Requirements",
                    "description": "Multiple compliance requirements to meet",
                    "severity": "MEDIUM",
                    "category": "Compliance",
                    "recommendation": "Create compliance checklist early"
                }
            ],
            "_model": "mock",
            "_tokens_used": 500,
            "_raw_response": json.dumps({"status": "mock_success"})
        }


ai_analyzer = AIAnalyzer()