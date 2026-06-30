"""
Request logging middleware.
"""
import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all requests with timing information."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Log request
            duration = time.time() - start_time
            logger.info(
                f"{method} {path}",
                extra={
                    "method": method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "client": client_host,
                    "user_agent": user_agent,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{method} {path} failed: {str(e)}",
                extra={
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration * 1000, 2),
                    "client": client_host,
                    "error": str(e)
                }
            )
            raise