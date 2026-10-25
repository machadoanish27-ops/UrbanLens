"""University and higher education service layer."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import ResourceNotFoundException
from app.db.repositories.city import CityRepository
from app.db.repositories.university import UniversityRepository


class UniversityService:
    """Service handling university institutions and global ranking datasets."""

    def __init__(self, database: Database) -> None:
        self.univ_repo = UniversityRepository(database)
        self.city_repo = CityRepository(database)

    def get_universities_by_city(
        self,
        city_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Fetch universities affiliated with the given city's regional context."""
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        country_iso2 = city.get("country_iso2")
        country_id = city.get("country_id")

        return self.univ_repo.get_universities_by_country(
            country_iso2=country_iso2,
            country_id=country_id,
            page=page,
            page_size=page_size,
        )

    def get_university(self, university_id: str) -> dict[str, Any]:
        """Fetch university details by unique identifier."""
        univ = self.univ_repo.get_by_university_id(university_id)
        if not univ:
            raise ResourceNotFoundException("university", university_id)
        rankings = self.univ_repo.get_rankings(university_id)
        univ["rankings"] = rankings
        return univ

    def get_university_rankings(
        self,
        university_id: str,
        ranking_metric: str | None = None,
        year: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch ranking history for an institution."""
        univ = self.univ_repo.get_by_university_id(university_id)
        if not univ:
            raise ResourceNotFoundException("university", university_id)
        return self.univ_repo.get_rankings(university_id, ranking_metric=ranking_metric, year=year)
