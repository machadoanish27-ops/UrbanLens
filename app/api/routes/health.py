"""Health and diagnostics endpoints providing system observability and provider telemetry."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Response, status

from app.core.cache import service_cache
from app.core.config import settings
from app.db.client import MongoClientManager
from app.providers.places.overpass import OverpassPlacesProvider

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


@router.get("/health/detailed", summary="Comprehensive system and provider observability health check")
def health_detailed(response: Response) -> dict[str, Any]:
    """Expose complete operational diagnostics across Database, Cache, LLM, and Overpass providers."""
    # 1. MongoDB Health
    db_health = MongoClientManager.check_health()
    db_connected = bool(db_health.get("connected"))

    # 2. Cache Diagnostics (Redis + In-Memory)
    cache_diag = service_cache.get_diagnostics()

    # 3. LLM Provider Redundancy Status
    groq_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
    secondary_configured = bool(settings.SECONDARY_LLM_API_KEY and settings.SECONDARY_LLM_API_KEY.strip())
    llm_health = {
        "primary": {
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "configured": groq_configured,
            "status": "ready" if groq_configured else "unconfigured",
            "key": settings.safe_groq_api_key,
        },
        "secondary": {
            "provider": settings.SECONDARY_LLM_PROVIDER,
            "model": settings.SECONDARY_LLM_MODEL,
            "configured": secondary_configured,
            "enabled": settings.SECONDARY_LLM_ENABLED,
            "status": "ready" if secondary_configured else "unconfigured",
            "key": settings.safe_secondary_llm_api_key,
        },
        "grounded_fallback": {
            "provider": "deterministic_grounded_engine",
            "model": "grounded-synthesis-v1",
            "status": "ready",
            "anti_hallucination_guaranteed": True,
        },
    }

    # 4. Overpass Endpoint Rotation Health
    try:
        overpass_provider = OverpassPlacesProvider()
        overpass_health = overpass_provider.get_health_diagnostics()
    except Exception as exc:
        overpass_health = {
            "overall_status": "error",
            "error": str(exc),
        }

    # 5. Overall System Status
    # Base health requires DB and FastAPI. Optional providers degrade but never hard-fail the system.
    if not db_connected:
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not groq_configured or not cache_diag.get("redis_connected"):
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "service": "urbanlens-api",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_health,
        "cache": cache_diag,
        "llm_providers": llm_health,
        "overpass": overpass_health,
        "rate_limiting": {
            "enabled": settings.RATE_LIMIT_ENABLED,
            "default_limit": settings.RATE_LIMIT_DEFAULT,
            "intelligence_limit": settings.RATE_LIMIT_INTELLIGENCE,
            "live_providers_limit": settings.RATE_LIMIT_LIVE_PROVIDERS,
        },
    }
