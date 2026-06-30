"""
Unit tests for models.
"""
import pytest
from app.models import User, Document, Risk, RiskSeverity, DocumentStatus


def test_create_user(db_session):
    """Test user creation."""
    user = User(
        azure_object_id="abc-123",
        email="test@company.com",
        display_name="Test User"
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.is_active is True
    assert user.created_at is not None


def test_create_document(db_session, test_user):
    """Test document creation."""
    doc = Document(
        owner_id=test_user.id,
        filename="rfp.pdf",
        storage_path="/tmp/rfp.pdf",
        file_size_bytes=1000,
        file_hash="hash123",
        status=DocumentStatus.UPLOADED.value
    )
    db_session.add(doc)
    db_session.commit()

    assert doc.id is not None
    assert doc.owner_id == test_user.id
    assert doc.status == "UPLOADED"


def test_create_risk(db_session, test_document):
    """Test risk creation."""
    risk = Risk(
        document_id=test_document.id,
        title="Tight deadline",
        description="30 day turnaround",
        severity=RiskSeverity.HIGH.value,
        category="Schedule"
    )
    db_session.add(risk)
    db_session.commit()

    assert risk.id is not None
    assert risk.document_id == test_document.id
    assert risk.severity == "HIGH"


def test_cascade_delete(db_session, test_document):
    """Test cascade delete."""
    risk = Risk(
        document_id=test_document.id,
        title="Test risk",
        description="Test description",
        severity=RiskSeverity.LOW.value
    )
    db_session.add(risk)
    db_session.commit()

    assert db_session.query(Risk).count() == 1

    db_session.delete(test_document)
    db_session.commit()

    assert db_session.query(Risk).count() == 0