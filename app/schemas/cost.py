"""Cost of living schemas."""

from pydantic import BaseModel, Field


class CostOfLivingMetricItem(BaseModel):
    """Specific cost-of-living basket metric."""

    city_id: str
    metric: str
    value: float | None = None
    unit: str | None = None
    observed_at: str | None = None
    source_id: str | None = None
    source_record_key: str | None = None


class CityCostOfLivingResponse(BaseModel):
    """Cost of living response for a city."""

    city_id: str
    is_available: bool = True
    metric_count: int = 0
    metrics: list[CostOfLivingMetricItem] = Field(default_factory=list)
