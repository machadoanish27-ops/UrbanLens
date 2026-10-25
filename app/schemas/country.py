"""Country response schemas."""

from pydantic import BaseModel, Field


class CountryItem(BaseModel):
    """Country record schema."""

    country_id: str
    iso2: str | None = None
    iso3: str | None = None
    name: str
    continent: str | None = None


class CountryDetail(CountryItem):
    """Detailed country record schema."""
    pass


class CountryMetricItem(BaseModel):
    """Socioeconomic or demographic metric for a country."""

    country_id: str
    iso2: str | None = None
    iso3: str | None = None
    metric: str
    period: int | None = None
    value: float | str | None = None
    unit: str | None = None
    source_id: str | None = None
    source_record_key: str | None = None


class CountryMetricsResponse(BaseModel):
    """Aggregated metrics for a country."""

    country_id: str
    metrics: list[CountryMetricItem] = Field(default_factory=list)
    gdp_metrics: list[CountryMetricItem] = Field(default_factory=list)
