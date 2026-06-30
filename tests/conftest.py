"""
Pytest configuration and fixtures.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ANTHROPIC_API_KEY"] = "test-key"
os.environ["AZURE_TENANT_ID"] = "test-tenant"
os.environ["AZURE_CLIENT_ID"] = "test-client"
os.environ["AZURE_CLIENT_SECRET"] = "test-secret"

from app.main import app
from app.core.database import Base, get_db


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.models import User
    user = User(
        azure_object_id="test-azure-oid",
        email="test@example.com",
        display_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_document(db_session, test_user):
    """Create a test document."""
    from app.models import Document
    doc = Document(
        owner_id=test_user.id,
        filename="test.pdf",
        storage_path="/tmp/test.pdf",
        file_size_bytes=1024,
        file_hash="testhash",
        status="UPLOADED"
    )
    db_session.add(doc)
    db_session.commit()
    return doc