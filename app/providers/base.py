"""Base abstractions for UrbanLens live external data providers."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger("providers.base")


class LiveStatus(str, Enum):
    """Normalized status of live data acquisition."""

    FRESH = "fresh"
    CACHED = "cached"
    DATABASE = "database"
    SECONDARY = "secondary"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class LiveMetadata(BaseModel):
    """Metadata attached to every provider response for strict provenance."""

    provider: str = Field(..., description="Provider identifier, e.g. open-meteo, openaq")
    source: str = Field(..., description="Canonical source information or endpoint URL")
    status: LiveStatus = Field(..., description="Data provenance status")
    fetched_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when data was fetched or evaluated",
    )
    observed_at: str | None = Field(
        default=None,
        description="ISO 8601 UTC timestamp of original observation when reported by source",
    )
    confidence: str | float | None = Field(
        default=None,
        description="Confidence level only when supported by source, never invented",
    )
    error_detail: str | None = Field(
        default=None,
        description="Non-sensitive error or unavailability diagnostic",
    )


T = TypeVar("T")


class ProviderResponse(BaseModel, Generic[T]):
    """Standard container wrapping provider payload with guaranteed metadata."""

    meta: LiveMetadata
    data: T | None = None

    @property
    def is_successful(self) -> bool:
        """Return True if fresh, cached, or database data is present."""
        return self.meta.status in (LiveStatus.FRESH, LiveStatus.CACHED, LiveStatus.DATABASE, LiveStatus.SECONDARY) and self.data is not None


class BaseProvider(ABC):
    """Abstract base class for replaceable live data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier."""
        ...

    @property
    @abstractmethod
    def source_info(self) -> str:
        """Provider source or documentation URL."""
        ...

    def create_meta(
        self,
        status: LiveStatus,
        observed_at: str | None = None,
        confidence: str | float | None = None,
        error_detail: str | None = None,
    ) -> LiveMetadata:
        """Construct normalized metadata for this provider."""
        return LiveMetadata(
            provider=self.provider_name,
            source=self.source_info,
            status=status,
            observed_at=observed_at,
            confidence=confidence,
            error_detail=error_detail,
        )
