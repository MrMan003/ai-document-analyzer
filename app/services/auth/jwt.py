"""
JWT token handling.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError

from app.core.config import settings


class JWTService:
    """JWT token service."""

    def create_session_token(self, user_id: str, email: str) -> tuple[str, int]:
        """Create a session JWT for a user."""
        expire_minutes = settings.JWT_EXPIRE_MINUTES
        expire_at = datetime.utcnow() + timedelta(minutes=expire_minutes)

        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire_at,
            "iat": datetime.utcnow(),
            "iss": settings.APP_NAME,
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return token, expire_minutes * 60

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT."""
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError:
            return None

    def refresh_token(self, token: str) -> Optional[tuple[str, int]]:
        """Refresh a token if it's still valid."""
        claims = self.decode_token(token)
        if not claims:
            return None

        # Check if token is expired
        exp = claims.get("exp")
        if exp and exp < datetime.utcnow().timestamp():
            return None

        # Create new token
        user_id = claims.get("sub")
        email = claims.get("email")
        if not user_id or not email:
            return None

        return self.create_session_token(user_id, email)

jwt_service = JWTService()