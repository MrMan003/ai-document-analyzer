"""
Global error handler middleware.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("error")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except AppException as e:
            logger.warning(
                f"Application error: {e.message}",
                extra={
                    "status_code": e.status_code,
                    "details": e.details,
                    "path": request.url.path
                }
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "details": e.details,
                    "status_code": e.status_code
                }
            )

        except Exception as e:
            logger.error(
                f"Unhandled error: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method
                },
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "An internal error occurred",
                    "status_code": 500
                }
            )