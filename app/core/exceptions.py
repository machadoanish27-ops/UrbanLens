"""Custom exception classes and FastAPI exception handlers."""

from typing import Any, Mapping
from fastapi import Request, status
from fastapi.responses import JSONResponse


class UrbanLensException(Exception):
    """Base exception for all UrbanLens domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(UrbanLensException):
    """Raised when an entity (city, country, university) is not found."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource.capitalize()} '{identifier}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
        )


class DataUnavailableException(UrbanLensException):
    """Raised when a specific data domain is unavailable for an entity."""

    def __init__(self, domain: str, identifier: str, reason: str = "No data recorded") -> None:
        super().__init__(
            message=f"Data for domain '{domain}' is unavailable for '{identifier}': {reason}.",
            code="DATA_UNAVAILABLE",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"domain": domain, "identifier": identifier, "reason": reason},
        )


class DatabaseUnavailableException(UrbanLensException):
    """Raised when the primary MongoDB database cannot be reached."""

    def __init__(self, reason: str = "Database connection unavailable") -> None:
        super().__init__(
            message="Database service is currently unreachable.",
            code="DATABASE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"reason": reason},
        )


class InvalidQueryException(UrbanLensException):
    """Raised when query parameters are malformed or invalid."""

    def __init__(self, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="INVALID_QUERY",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


async def urbanlens_exception_handler(request: Request, exc: UrbanLensException) -> JSONResponse:
    """Render UrbanLensException into standard JSON error response."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
            "meta": {
                "request_id": request_id,
            },
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled server errors (never exposes internal traceback)."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": {},
            },
            "meta": {
                "request_id": request_id,
            },
        },
    )
