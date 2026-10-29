"""Country repository accessing countries, country metrics, and GDP metrics."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class CountryRepository(BaseRepository):
    """Repository for country records and country-level socioeconomic metrics."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "countries")
        self.metrics_repo = BaseRepository(database, "country_metrics")
        self.gdp_repo = BaseRepository(database, "gdp_country_metrics")

    def get_by_country_id(self, country_id: str) -> dict[str, Any] | None:
        """Fetch country record by canonical country_id or ISO2/ISO3."""
        cid = country_id.strip()
        doc = self.find_one({"country_id": cid})
        if not doc and cid.startswith("country_") and len(cid) == 10:
            prefix, code = cid.split("_", 1)
            doc = self.find_one({"country_id": f"{prefix}_{code.upper()}"})
        if not doc:
            # Fallback by uppercase ISO codes
            doc = self.find_one({"$or": [{"iso2": country_id.upper()}, {"iso3": country_id.upper()}]})
        return doc

    def list_countries(
        self,
        continent: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """List countries with optional continent filtering and pagination."""
        filters: dict[str, Any] = {}
        if continent:
            filters["continent"] = continent.strip()
        sort = [("name", 1)]
        return self.find_paginated(filters, sort=sort, page=page, page_size=page_size)

    def get_metrics(
        self,
        country_id: str,
        metric: str | None = None,
        period: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch general country metrics."""
        cid = country_id.strip()
        if cid.startswith("country_") and len(cid) == 10:
            prefix, code = cid.split("_", 1)
            canonical_cid = f"{prefix}_{code.upper()}"
        else:
            canonical_cid = cid
        filters: dict[str, Any] = {"country_id": canonical_cid}
        if metric:
            filters["metric"] = metric
        if period is not None:
            filters["period"] = period
        return self.metrics_repo.find_many(filters, sort=[("metric", 1), ("period", -1)])

    def get_gdp_metrics(
        self,
        country_id: str,
        period: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch GDP country metrics."""
        cid = country_id.strip()
        if cid.startswith("country_") and len(cid) == 10:
            prefix, code = cid.split("_", 1)
            canonical_cid = f"{prefix}_{code.upper()}"
        else:
            canonical_cid = cid
        filters: dict[str, Any] = {"country_id": canonical_cid}
        if period is not None:
            filters["period"] = period
        return self.gdp_repo.find_many(filters, sort=[("period", -1)])
