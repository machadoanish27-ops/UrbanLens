"""University and rankings schemas."""

from pydantic import BaseModel, Field


class UniversityItem(BaseModel):
    """Higher education institution record."""

    university_id: str
    name: str
    country_iso2: str | None = None
    website: str | None = None
    country_id: str | None = None
    source_id: str | None = None
    country_iso3: str | None = None


class UniversityRankingItem(BaseModel):
    """University global ranking entry with provenance and unavailable flag."""

    university_id: str
    university_name: str | None = None
    country_iso2: str | None = None
    ranking_metric: str
    ranking_year: int | None = None
    value: int | float | str | None = None
    unavailable: bool | None = None
    source_id: str | None = None
    source_record_key: str | None = None


class UniversityDetail(UniversityItem):
    """University detail with associated ranking history."""

    rankings: list[UniversityRankingItem] = Field(default_factory=list)
