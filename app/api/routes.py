"""Compatibility router module delegating to full routes package."""

from fastapi import APIRouter
from app.api.routes import api_v1_router, root_router

# Combined router for backward compatibility
router = APIRouter()
router.include_router(root_router)
router.include_router(api_v1_router)

__all__ = ["router", "root_router", "api_v1_router"]
