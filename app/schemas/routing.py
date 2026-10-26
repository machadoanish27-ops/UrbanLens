"""Routing response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class RouteResponse(BaseModel):
    """Response payload for waypoint-to-waypoint routing."""

    origin: dict[str, float]
    destination: dict[str, float]
    route: dict[str, Any] | None = None
    meta: dict[str, Any]
