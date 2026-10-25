"""Health and diagnostics endpoints."""

from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.db.client import MongoClientManager

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic API application health check")
def health() -> dict[str, str]:
    """Verify that the FastAPI application is alive and responding."""
    return {
        "status": "ok",
        "service": "urbanlens-api",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/db", summary="MongoDB connectivity health check")
def health_db(response: Response) -> dict[str, object]:
    """Verify MongoDB Atlas connectivity without exposing internal credentials or secrets."""
    health_status = MongoClientManager.check_health()
    if not health_status.get("connected"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health_status
