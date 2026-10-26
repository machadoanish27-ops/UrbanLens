"""Public transit feed response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class TransitFeedResponse(BaseModel):
    """Response payload for public transit feed status."""

    city_id: str
    city_name: str | None = None
    transit: dict[str, Any] | None = None
    meta: dict[str, Any]
