"""
Unit tests for authentication.
"""
import pytest
from app.services.auth import jwt_service


def test_create_session_token():
    """Test JWT creation."""
    token, expires_in = jwt_service.create_session_token("user-123", "test@example.com")
    assert token is not None
    assert expires_in > 0


def test_decode_valid_token():
    """Test decoding a valid token."""
    token, _ = jwt_service.create_session_token("user-123", "test@example.com")
    claims = jwt_service.decode_token(token)
    assert claims is not None
    assert claims["sub"] == "user-123"
    assert claims["email"] == "test@example.com"


def test_decode_invalid_token():
    """Test decoding an invalid token."""
    assert jwt_service.decode_token("invalid-token") is None


def test_refresh_token():
    """Test token refresh."""
    token, _ = jwt_service.create_session_token("user-123", "test@example.com")
    result = jwt_service.refresh_token(token)
    assert result is not None
    new_token, expires_in = result
    assert new_token != token