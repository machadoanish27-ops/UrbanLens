"""Application rate limiting configuration and structured 429 response handling."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

logger = logging.getLogger("app.core.rate_limit")


def get_client_identifier(request: Request) -> str:
    """Determine client identifier using X-Forwarded-For or remote socket address."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the leftmost IP (client)
        client_ip = forwarded.split(",")[0].strip()
        if client_ip:
            return client_ip
    return get_remote_address(request) or "127.0.0.1"


# Initialize Limiter with Redis storage if enabled, otherwise in-memory storage
storage_uri = (
    settings.REDIS_URL
    if (settings.REDIS_ENABLED and settings.REDIS_URL)
    else "memory://"
)

try:
    limiter = Limiter(
        key_func=get_client_identifier,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri=storage_uri,
        enabled=settings.RATE_LIMIT_ENABLED,
    )
    logger.info("Initialized rate limiter with backend '%s'", "redis" if "redis" in storage_uri else "memory")
except Exception as exc:
    logger.warning("Failed initializing rate limiter with URI '%s': %s. Falling back to memory://", storage_uri, exc)
    limiter = Limiter(
        key_func=get_client_identifier,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri="memory://",
        enabled=settings.RATE_LIMIT_ENABLED,
    )


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Transform rate limit violation into standard UrbanLens ApiResponse format with HTTP 429."""
    limit_detail = str(exc.detail) if exc.detail else "Rate limit threshold reached"
    logger.warning("Rate limit exceeded for %s on %s: %s", get_client_identifier(request), request.url.path, limit_detail)

    response_payload = {
        "success": False,
        "data": None,
        "error": {
            "code": "RATE_LIMIT_EXCEEDED",
            "message": f"Too many requests: {limit_detail}. Please slow down your queries.",
            "details": {"limit": limit_detail, "path": request.url.path},
        },
        "meta": {
            "source": "gateway_rate_limiter",
            "status": "rate_limited",
            "retry_after_seconds": 60,
        },
    }

    return JSONResponse(
        status_code=429,
        content=response_payload,
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": limit_detail,
        },
    )
