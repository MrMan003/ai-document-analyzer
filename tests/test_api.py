"""
API endpoint tests.
"""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_redirect(client):
    """Test login redirect."""
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "login.microsoftonline.com" in response.headers["location"]


def test_me_requires_auth(client):
    """Test that /me requires authentication."""
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_upload_requires_auth(client):
    """Test that upload requires authentication."""
    response = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 fake", "application/pdf")}
    )
    assert response.status_code in (401, 403)