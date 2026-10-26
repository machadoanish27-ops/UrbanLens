"""Pytest fixtures and test client setup."""

from typing import Any
import pytest
from fastapi.testclient import TestClient

from app.db.client import get_db
from app.main import app


class MockCollection:
    """In-memory mock for a MongoDB collection supporting common test operations."""

    def __init__(self, name: str, documents: list[dict[str, Any]] | None = None) -> None:
        self.name = name
        self.documents = documents or []

    def _matches(self, doc: dict[str, Any], query: dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "$or" and isinstance(v, list):
                if not any(self._matches(doc, cond) for cond in v):
                    return False
            elif isinstance(v, dict):
                field_val = doc.get(k)
                for op, op_val in v.items():
                    if op == "$in" and (field_val not in op_val):
                        return False
                    if op == "$exists":
                        exists = k in doc
                        if exists != op_val:
                            return False
                    if op == "$gte" and (field_val is None or field_val < op_val):
                        return False
                    if op == "$lte" and (field_val is None or field_val > op_val):
                        return False
                    if op == "$regex":
                        import re
                        options = v.get("$options", "")
                        flags = re.IGNORECASE if "i" in options else 0
                        if field_val is None or not re.search(op_val, str(field_val), flags):
                            return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def find(self, query: dict[str, Any] | None = None, projection: Any = None) -> "MockCursor":
        query = query or {}
        matched = [d.copy() for d in self.documents if self._matches(d, query)]
        return MockCursor(matched)

    def count_documents(self, query: dict[str, Any] | None = None) -> int:
        query = query or {}
        return sum(1 for d in self.documents if self._matches(d, query))

    def replace_one(self, query: dict[str, Any], replacement: dict[str, Any], upsert: bool = False) -> Any:
        class ReplaceResult:
            def __init__(self, matched: int, modified: int, upserted_id: Any = None):
                self.matched_count = matched
                self.modified_count = modified
                self.upserted_id = upserted_id
        for idx, d in enumerate(self.documents):
            if self._matches(d, query):
                self.documents[idx] = replacement.copy()
                return ReplaceResult(1, 1)
        if upsert:
            self.documents.append(replacement.copy())
            return ReplaceResult(0, 0, replacement.get("_id") or replacement.get("id"))
        return ReplaceResult(0, 0)

    def delete_one(self, query: dict[str, Any]) -> Any:
        class DeleteResult:
            def __init__(self, count: int):
                self.deleted_count = count
        for idx, d in enumerate(self.documents):
            if self._matches(d, query):
                self.documents.pop(idx)
                return DeleteResult(1)
        return DeleteResult(0)

    def delete_many(self, query: dict[str, Any]) -> Any:
        class DeleteResult:
            def __init__(self, count: int):
                self.deleted_count = count
        orig_len = len(self.documents)
        self.documents = [d for d in self.documents if not self._matches(d, query)]
        return DeleteResult(orig_len - len(self.documents))

    def create_index(self, *args, **kwargs) -> str:
        return "index_ok"


class MockCursor:
    """Mock MongoDB cursor supporting sort, skip, limit, and iteration."""

    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = list(docs)
        self._iter = iter(self._docs)

    def sort(self, key_or_list: Any, direction: int | None = None) -> "MockCursor":
        if isinstance(key_or_list, list) and key_or_list:
            sort_field, sort_dir = key_or_list[0]
            reverse = sort_dir == -1
            self._docs.sort(key=lambda d: (d.get(sort_field) is None, d.get(sort_field, 0)), reverse=reverse)
        self._iter = iter(self._docs)
        return self

    def skip(self, n: int) -> "MockCursor":
        self._docs = self._docs[n:]
        self._iter = iter(self._docs)
        return self

    def limit(self, n: int) -> "MockCursor":
        self._docs = self._docs[:n]
        self._iter = iter(self._docs)
        return self

    def __iter__(self) -> "MockCursor":
        return self

    def __next__(self) -> dict[str, Any]:
        return next(self._iter)


class MockDatabase:
    """In-memory mock database populated with sample canonical test fixtures."""

    def __init__(self) -> None:
        self.collections: dict[str, MockCollection] = {
            "cities": MockCollection("cities", [
                {
                    "_id": "60a1",
                    "city_id": "tokyo_jp",
                    "worldcities_id": 1392685764,
                    "name": "Tokyo",
                    "name_ascii": "Tokyo",
                    "country_id": "japan",
                    "country_iso2": "JP",
                    "country_iso3": "JPN",
                    "admin_name": "Tokyo",
                    "capital": "primary",
                    "population": 37977000,
                    "latitude": 35.6897,
                    "longitude": 139.6922,
                },
                {
                    "_id": "60a2",
                    "city_id": "paris_fr",
                    "worldcities_id": 1250015082,
                    "name": "Paris",
                    "name_ascii": "Paris",
                    "country_id": "france",
                    "country_iso2": "FR",
                    "country_iso3": "FRA",
                    "admin_name": "Île-de-France",
                    "capital": "primary",
                    "population": 11020000,
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                },
            ]),
            "city_aliases": MockCollection("city_aliases", [
                {"city_id": "tokyo_jp", "alias": "Tokio", "normalized_alias": "tokio"},
                {"city_id": "paris_fr", "alias": "City of Light", "normalized_alias": "city of light"},
            ]),
            "city_provider_identities": MockCollection("city_provider_identities", [
                {"city_id": "tokyo_jp", "provider": "weather", "provider_location_id": "tokyo_weather_01"},
            ]),
            "countries": MockCollection("countries", [
                {"country_id": "japan", "iso2": "JP", "iso3": "JPN", "name": "Japan", "continent": "Asia"},
                {"country_id": "france", "iso2": "FR", "iso3": "FRA", "name": "France", "continent": "Europe"},
            ]),
            "country_metrics": MockCollection("country_metrics", [
                {"country_id": "japan", "iso2": "JP", "iso3": "JPN", "metric": "Life Expectancy", "period": 2022, "value": 84.6, "unit": "years"},
            ]),
            "gdp_country_metrics": MockCollection("gdp_country_metrics", [
                {"country_id": "japan", "iso2": "JP", "iso3": "JPN", "metric": "GDP", "period": 2022, "value": 4232.0, "unit": "billion_usd"},
            ]),
            "weather_observations": MockCollection("weather_observations", [
                {
                    "city_id": "tokyo_jp",
                    "provider": "global_weather",
                    "observed_at": "2026-10-25T12:00:00Z",
                    "temperature_c": 19.5,
                    "humidity_pct": 65.0,
                    "pressure_mb": 1013.2,
                    "wind_kph": 12.0,
                    "precip_mm": 0.0,
                    "visibility_km": 10.0,
                    "uv_index": 4.0,
                    "source_row": 1,
                }
            ]),
            "weather_forecasts_wmo": MockCollection("weather_forecasts_wmo", [
                {
                    "city_id": "tokyo_jp",
                    "provider": "WMO",
                    "forecast_for": "2026-10-26T00:00:00Z",
                    "fetched_at": "2026-10-25T06:00:00Z",
                    "forecast_min_temp_c": 14.0,
                    "forecast_max_temp_c": 22.0,
                    "condition": "Clear",
                    "description": "Sunny conditions",
                    "timezone": "Asia/Tokyo",
                }
            ]),
            "air_quality_observations_global_weather": MockCollection("air_quality_observations_global_weather", [
                {
                    "city_id": "tokyo_jp",
                    "provider": "global_weather",
                    "observed_at": "2026-10-25T12:00:00Z",
                    "aqi_us_epa": 2,
                    "pm25": 12.5,
                    "pm10": 20.0,
                    "no2": 15.0,
                    "so2": 2.0,
                    "o3": 35.0,
                    "co": 300.0,
                    "source_row": 1,
                }
            ]),
            "air_quality_observations_who": MockCollection("air_quality_observations_who", [
                {
                    "city_id": "tokyo_jp",
                    "source": "WHO",
                    "year": 2022,
                    "pm25_annual_mean_ug_m3": 11.2,
                    "pm10_annual_mean_ug_m3": 18.4,
                    "pm25_temporal_coverage": "95%",
                    "pm10_temporal_coverage": "95%",
                    "source_row": 1,
                }
            ]),
            "cost_of_living": MockCollection("cost_of_living", [
                {
                    "city_id": "tokyo_jp",
                    "metric": "Meal, Inexpensive Restaurant",
                    "value": 1000.0,
                    "unit": "JPY",
                    "observed_at": "2026-01-01",
                    "source_id": "numbeo",
                    "source_record_key": "tokyo_meal_inexpensive",
                },
                {
                    "city_id": "tokyo_jp",
                    "metric": "Apartment (1 bedroom) in City Centre",
                    "value": 140000.0,
                    "unit": "JPY",
                    "observed_at": "2026-01-01",
                    "source_id": "numbeo",
                    "source_record_key": "tokyo_apartment_1bed",
                },
            ]),
            "universities": MockCollection("universities", [
                {
                    "university_id": "u_tokyo",
                    "name": "University of Tokyo",
                    "country_iso2": "JP",
                    "country_id": "japan",
                    "website": "https://www.u-tokyo.ac.jp",
                }
            ]),
            "university_rankings": MockCollection("university_rankings", [
                {
                    "university_id": "u_tokyo",
                    "university_name": "University of Tokyo",
                    "country_iso2": "JP",
                    "ranking_metric": "QS World University Rankings",
                    "ranking_year": 2024,
                    "value": 28,
                    "unavailable": False,
                    "source_id": "qs_2024",
                }
            ]),
            "source_registry": MockCollection("source_registry", [
                {"source_id": "numbeo", "source_file": "cost_of_living.csv", "source_type": "cost"}
            ]),
        }

    def __getitem__(self, name: str) -> MockCollection:
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]


@pytest.fixture
def mock_db() -> MockDatabase:
    """Fixture providing an in-memory mock database."""
    return MockDatabase()


@pytest.fixture
def client(mock_db: MockDatabase) -> TestClient:
    """FastAPI TestClient with database dependency overridden by mock_db."""
    app.dependency_overrides[get_db] = lambda: mock_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_service_cache():
    """Clear service-layer in-memory cache between all test runs for strict test isolation."""
    from app.core.cache import service_cache
    service_cache.clear()
    yield
    service_cache.clear()

