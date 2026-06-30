"""
Shared enumerations for the application.
"""
from enum import Enum


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskCategory(str, Enum):
    FINANCIAL = "Financial"
    LEGAL = "Legal"
    TECHNICAL = "Technical"
    SCHEDULE = "Schedule"
    COMPLIANCE = "Compliance"
    OPERATIONAL = "Operational"
    REPUTATIONAL = "Reputational"
    OTHER = "Other"


class DocumentType(str, Enum):
    RFP = "RFP"
    TENDER = "Tender"
    CONTRACT = "Contract"
    PROPOSAL = "Proposal"
    OTHER = "Other"


class AuditAction(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    VIEW_DOCUMENT = "VIEW_DOCUMENT"
    DELETE_DOCUMENT = "DELETE_DOCUMENT"
    PROCESS_DOCUMENT = "PROCESS_DOCUMENT"
    REPROCESS_DOCUMENT = "REPROCESS_DOCUMENT"
    EXPORT_DOCUMENT = "EXPORT_DOCUMENT"
    SHARE_DOCUMENT = "SHARE_DOCUMENT"
    USER_ADMIN = "USER_ADMIN"


class MitigationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    MITIGATED = "MITIGATED"
    ACCEPTED = "ACCEPTED"