"""University repository accessing universities and rankings collections."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class UniversityRepository(BaseRepository):
    """Repository for higher education institutions and rankings."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "universities")
        self.rankings_repo = BaseRepository(database, "university_rankings")

    def get_by_university_id(self, university_id: str) -> dict[str, Any] | None:
        """Fetch a university by its unique university_id."""
        return self.find_one({"university_id": university_id})

    def get_universities_by_country(
        self,
        country_iso2: str | None = None,
        country_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Fetch universities matching country criteria."""
        filters: dict[str, Any] = {}
        if country_iso2:
            filters["country_iso2"] = country_iso2.strip().upper()
        if country_id:
            raw = country_id.strip()
            if raw.startswith("country_") and len(raw) == 10:
                prefix, code = raw.split("_", 1)
                canonical_country_id = f"{prefix}_{code.upper()}"
            else:
                canonical_country_id = raw
            filters["country_id"] = canonical_country_id
        sort = [("name", 1)]
        return self.find_paginated(filters, sort=sort, page=page, page_size=page_size)

    def search_universities(
        self,
        query: str | None = None,
        country_iso2: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search universities by name and/or country."""
        filters: dict[str, Any] = {}
        if query:
            import re
            filters["name"] = {"$regex": re.escape(query.strip()), "$options": "i"}
        if country_iso2:
            filters["country_iso2"] = country_iso2.strip().upper()
        sort = [("name", 1)]
        return self.find_paginated(filters, sort=sort, page=page, page_size=page_size)

    def get_rankings(
        self,
        university_id: str,
        ranking_metric: str | None = None,
        year: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch rankings for a university with provenance and unavailable flags."""
        filters: dict[str, Any] = {"university_id": university_id}
        if ranking_metric:
            filters["ranking_metric"] = ranking_metric
        if year is not None:
            filters["ranking_year"] = year
        return self.rankings_repo.find_many(filters, sort=[("ranking_year", -1), ("ranking_metric", 1)])
