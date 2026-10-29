"""Country response schemas."""

from pydantic import BaseModel, Field


class CountryItem(BaseModel):
    """Country record schema."""

    country_id: str
    iso2: str | None = None
    iso3: str | None = None
    name: str
    continent: str | None = None


class CountryLanguageInfo(BaseModel):
    """Authoritative language and cultural metadata with source provenance."""

    country_id: str
    country_iso2: str | None = None
    status: str = "available"
    official_languages: list[str] = Field(default_factory=list)
    spoken_languages: list[str] = Field(default_factory=list)
    language_codes: list[str] = Field(default_factory=list)
    cultural_notes: str | None = None
    source: str | None = "ISO-639 / UN Linguistic Statistics & UNESCO World Languages"
    source_url: str | None = "https://www.iso.org/iso-639-language-codes.html"
    level: str = "country"


class CountryDetail(CountryItem):
    """Detailed country record schema."""

    languages: CountryLanguageInfo | None = None


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
