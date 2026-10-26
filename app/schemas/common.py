"""Standard API response, metadata, and pagination schemas."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata model."""

    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total matching items")
    total_pages: int = Field(..., ge=0, description="Total pages available")
    has_next: bool = Field(..., description="Whether there is a subsequent page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> "PaginationMeta":
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class ResponseMeta(BaseModel):
    """Metadata accompanying all API responses."""

    request_id: str | None = Field(default=None, description="Unique trace identifier")
    fetched_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when the response was generated",
    )
    source: str | None = Field(default="UrbanLens MongoDB Engine", description="Source provider or subsystem")
    pagination: PaginationMeta | None = Field(default=None, description="Pagination metadata if applicable")


class ApiResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""

    success: bool = Field(default=True, description="Indicates request success")
    data: T = Field(..., description="Payload data")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="Response metadata")


class ApiErrorDetail(BaseModel):
    """Detailed error object."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable description of the error")
    details: dict[str, Any] | None = Field(default=None, description="Contextual error details")


class ApiErrorResponse(BaseModel):
    """Standard error response structure."""

    success: bool = Field(default=False, description="Always false on error")
    error: ApiErrorDetail = Field(..., description="Error description")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="Response metadata")


class ProvenanceInfo(BaseModel):
    """Source-grounded provenance metadata preserved for data points."""

    source_id: str | None = None
    provider: str | None = None
    observed_at: str | None = None
    fetched_at: str | None = None
    confidence: str | float | None = None
    source_row: int | None = None
    source_record_key: str | None = None
