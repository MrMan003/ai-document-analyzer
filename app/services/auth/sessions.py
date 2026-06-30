"""
Session management with Redis.
"""
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.cache import cache


class SessionService:
    """Session management service using Redis."""

    SESSION_PREFIX = "session:"
    SESSION_TTL = 480 * 60  # 8 hours in seconds

    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create a new session."""
        session_id = f"{self.SESSION_PREFIX}{user_id}:{datetime.utcnow().timestamp()}"
        data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **session_data
        }
        await cache.set(session_id, data, ttl=self.SESSION_TTL)
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        return await cache.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return await cache.delete(session_id)

    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user."""
        pattern = f"{self.SESSION_PREFIX}{user_id}:*"
        return await cache.clear_pattern(pattern)

    async def extend_session(self, session_id: str) -> bool:
        """Extend session TTL."""
        session = await self.get_session(session_id)
        if session:
            return await cache.set(session_id, session, ttl=self.SESSION_TTL)
        return False

session_service = SessionService()