"""
Redis cache abstraction layer.
"""
import json
from typing import Any, Optional, Callable
import redis.asyncio as redis
from app.core.config import settings


class Cache:
    """Async Redis cache client."""

    def __init__(self):
        self.client = None

    async def connect(self):
        """Establish Redis connection."""
        if self.client is None:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
        return self.client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        client = await self.connect()
        value = await client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        client = await self.connect()
        serialized = json.dumps(value, default=str)
        return await client.setex(key, ttl, serialized)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        client = await self.connect()
        return await client.delete(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        client = await self.connect()
        keys = await client.keys(pattern)
        if keys:
            return await client.delete(*keys)
        return 0

    async def get_or_set(self, key: str, callback: Callable, ttl: int = 3600) -> Any:
        """Get value or set if not exists."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await callback()
        await self.set(key, value, ttl)
        return value


cache = Cache()