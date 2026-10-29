"""Country service layer."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import ResourceNotFoundException
from app.db.repositories.country import CountryRepository
from app.data.languages import get_country_languages


class CountryService:
    """Service handling country metadata and national macroeconomic metrics."""

    def __init__(self, database: Database) -> None:
        self.country_repo = CountryRepository(database)

    def list_countries(
        self,
        continent: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """List countries with optional continent filter."""
        return self.country_repo.list_countries(continent=continent, page=page, page_size=page_size)

    def get_country(self, country_id: str) -> dict[str, Any]:
        """Fetch a specific country by identifier or ISO code."""
        country = self.country_repo.get_by_country_id(country_id)
        if not country:
            raise ResourceNotFoundException("country", country_id)
        country["languages"] = get_country_languages(country.get("iso2") or country.get("country_id"), iso2_hint=country.get("iso2"))
        return country

    def get_country_languages(self, country_id: str) -> dict[str, Any]:
        """Fetch authoritative language metadata for a country."""
        country = self.get_country(country_id)
        return get_country_languages(country.get("iso2") or country.get("country_id"), iso2_hint=country.get("iso2"))

    def get_country_metrics(
        self,
        country_id: str,
        metric: str | None = None,
        period: int | None = None,
    ) -> dict[str, Any]:
        """Fetch all socioeconomic and GDP metrics for a country."""
        country = self.get_country(country_id)
        cid = country["country_id"]

        metrics = self.country_repo.get_metrics(cid, metric=metric, period=period)
        gdp_metrics = self.country_repo.get_gdp_metrics(cid, period=period)

        return {
            "country_id": cid,
            "metrics": metrics,
            "gdp_metrics": gdp_metrics,
        }
