"""City intelligence service layer."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import ResourceNotFoundException
from app.db.repositories.city import CityRepository
from app.db.repositories.country import CountryRepository
from app.db.repositories.weather import WeatherRepository
from app.db.repositories.air_quality import AirQualityRepository
from app.db.repositories.cost_of_living import CostOfLivingRepository
from app.db.repositories.university import UniversityRepository


class CityService:
    """Service orchestrating city entity retrieval, search, and multidimensional overview."""

    def __init__(self, database: Database) -> None:
        self.city_repo = CityRepository(database)
        self.country_repo = CountryRepository(database)
        self.weather_repo = WeatherRepository(database)
        self.aq_repo = AirQualityRepository(database)
        self.cost_repo = CostOfLivingRepository(database)
        self.univ_repo = UniversityRepository(database)

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
        """Search cities with filtering and pagination."""
        # Check if query matches an alias
        if query and not country_id and not country_iso2:
            resolved_city_id = self.city_repo.resolve_alias_to_city_id(query)
            if resolved_city_id:
                city = self.city_repo.get_by_city_id(resolved_city_id)
                if city:
                    return [city], 1

        return self.city_repo.search_cities(
            query=query,
            country_id=country_id,
            country_iso2=country_iso2,
            country_iso3=country_iso3,
            min_population=min_population,
            max_population=max_population,
            page=page,
            page_size=page_size,
        )

    def get_city_details(self, city_id: str) -> dict[str, Any]:
        """Fetch canonical city entity along with aliases and provider identities."""
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            # Check if this identifier is an alias
            resolved_id = self.city_repo.resolve_alias_to_city_id(city_id)
            if resolved_id:
                city = self.city_repo.get_by_city_id(resolved_id)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        canonical_id = city["city_id"]
        aliases = self.city_repo.get_aliases(canonical_id)
        identities = self.city_repo.get_provider_identities(canonical_id)

        city["aliases"] = aliases
        city["provider_identities"] = identities
        return city

    def get_city_overview(self, city_id: str) -> dict[str, Any]:
        """Synthesize multidimensional overview for a city without fabricating missing data."""
        city_details = self.get_city_details(city_id)
        canonical_id = city_details["city_id"]

        # Weather snapshot
        latest_weather = self.weather_repo.get_latest_observation(canonical_id)
        weather_summary = None
        if latest_weather:
            weather_summary = {
                "provider": latest_weather.get("provider"),
                "observed_at": latest_weather.get("observed_at"),
                "temperature_c": latest_weather.get("temperature_c"),
                "humidity_pct": latest_weather.get("humidity_pct"),
                "wind_kph": latest_weather.get("wind_kph"),
                "precip_mm": latest_weather.get("precip_mm"),
            }

        # Air quality snapshot
        latest_aq_gw = self.aq_repo.get_latest_global_weather_aq(canonical_id)
        latest_aq_who = self.aq_repo.get_latest_who_aq(canonical_id)
        aq_summary = None
        if latest_aq_gw or latest_aq_who:
            aq_summary = {}
            if latest_aq_gw:
                aq_summary["global_weather"] = {
                    "provider": latest_aq_gw.get("provider"),
                    "observed_at": latest_aq_gw.get("observed_at"),
                    "aqi_us_epa": latest_aq_gw.get("aqi_us_epa"),
                    "pm25": latest_aq_gw.get("pm25"),
                    "pm10": latest_aq_gw.get("pm10"),
                }
            if latest_aq_who:
                aq_summary["who_annual"] = {
                    "source": latest_aq_who.get("source"),
                    "year": latest_aq_who.get("year"),
                    "pm25_annual_mean_ug_m3": latest_aq_who.get("pm25_annual_mean_ug_m3"),
                    "pm10_annual_mean_ug_m3": latest_aq_who.get("pm10_annual_mean_ug_m3"),
                }

        # Cost of living snapshot
        cost_metrics = self.cost_repo.get_by_city_id(canonical_id)
        cost_summary = None
        if cost_metrics:
            cost_summary = {
                "available": True,
                "recorded_metrics_count": len(cost_metrics),
                "highlights": {m["metric"]: m.get("value") for m in cost_metrics[:5] if "metric" in m},
            }
        else:
            cost_summary = {"available": False, "recorded_metrics_count": 0}

        # Universities snapshot
        country_iso2 = city_details.get("country_iso2")
        univ_items, univ_count = ([], 0)
        if country_iso2:
            univ_items, univ_count = self.univ_repo.get_universities_by_country(
                country_iso2=country_iso2, page=1, page_size=5
            )
        univ_summary = {
            "country_institutions_count": univ_count,
            "sample_institutions": [u.get("name") for u in univ_items],
        }

        # Country snapshot
        country_id = city_details.get("country_id")
        country_summary = None
        if country_id:
            country_doc = self.country_repo.get_by_country_id(country_id)
            if country_doc:
                country_summary = {
                    "country_id": country_doc.get("country_id"),
                    "name": country_doc.get("name"),
                    "continent": country_doc.get("continent"),
                    "iso2": country_doc.get("iso2"),
                    "iso3": country_doc.get("iso3"),
                }

        return {
            "city": city_details,
            "weather_summary": weather_summary,
            "air_quality_summary": aq_summary,
            "cost_of_living_summary": cost_summary,
            "universities_summary": univ_summary,
            "country_summary": country_summary,
        }
