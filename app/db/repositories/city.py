"""City repository accessing cities, aliases, and provider identities."""

import re
from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class CityRepository(BaseRepository):
    """Repository for city records, aliases, and provider identities."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "cities")
        self.aliases_repo = BaseRepository(database, "city_aliases")
        self.identities_repo = BaseRepository(database, "city_provider_identities")

    def get_by_city_id(self, city_id: str) -> dict[str, Any] | None:
        """Fetch city record by canonical city_id."""
        return self.find_one({"city_id": city_id})

    def get_aliases(self, city_id: str) -> list[dict[str, Any]]:
        """Fetch all recognized aliases for a city."""
        return self.aliases_repo.find_many({"city_id": city_id})

    def get_provider_identities(self, city_id: str) -> list[dict[str, Any]]:
        """Fetch provider-specific identities for a city."""
        return self.identities_repo.find_many({"city_id": city_id})

    def resolve_alias_to_city_id(self, alias: str) -> str | None:
        """Resolve an alias string to canonical city_id."""
        normalized = alias.strip().lower()
        rec = self.aliases_repo.find_one({"normalized_alias": normalized})
        if rec and "city_id" in rec:
            return str(rec["city_id"])
        return None

    def search_cities(
        self,
        query: str | None = None,
        country_id: str | None = None,
        country_iso2: str | None = None,
        country_iso3: str | None = None,
        min_population: int | None = None,
        max_population: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search cities with flexible filtering and pagination."""
        filters: dict[str, Any] = {}

        if query:
            escaped = re.escape(query.strip())
            filters["$or"] = [
                {"name": {"$regex": f"^{escaped}", "$options": "i"}},
                {"name_ascii": {"$regex": f"^{escaped}", "$options": "i"}},
                {"city_id": query.strip().lower()},
            ]

        if country_id:
            filters["country_id"] = country_id.strip().lower()
        if country_iso2:
            filters["country_iso2"] = country_iso2.strip().upper()
        if country_iso3:
            filters["country_iso3"] = country_iso3.strip().upper()

        if min_population is not None or max_population is not None:
            pop_filter: dict[str, Any] = {}
            if min_population is not None:
                pop_filter["$gte"] = min_population
            if max_population is not None:
                pop_filter["$lte"] = max_population
            filters["population"] = pop_filter

        sort = [("population", -1), ("name", 1)]
        return self.find_paginated(filters, sort=sort, page=page, page_size=page_size)
