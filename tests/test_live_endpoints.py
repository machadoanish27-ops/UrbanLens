"""Unit tests for live intelligence API endpoints using TestClient and mocked providers."""

import pytest
from fastapi.testclient import TestClient

from app.db.client import get_db
from app.main import app
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.weather import (
    BaseWeatherProvider,
    NormalizedCurrentWeather,
    NormalizedWeather,
)
from app.providers.air_quality import (
    BaseAirQualityProvider,
    NormalizedAirQuality,
    NormalizedPollutants,
)
from app.providers.currency import (
    BaseCurrencyProvider,
    NormalizedCurrencyConversion,
)
from app.providers.geocoding import (
    BaseGeocodingProvider,
    NormalizedGeocodingItem,
)
from app.providers.routing import (
    BaseRoutingProvider,
    NormalizedRoute,
)
from app.providers.places import (
    BasePlacesProvider,
    NormalizedPlaceItem,
)
from app.providers.transit import (
    BaseTransitProvider,
    NormalizedTransitFeedInfo,
)
from app.services.air_quality import AirQualityService
from app.services.currency import CurrencyService
from app.services.geocoding import GeocodingService
from app.services.places import PlacesService
from app.services.routing import RoutingService
from app.services.transit import TransitService
from app.services.weather import WeatherService
from tests.conftest import MockDatabase


@pytest.fixture
def mock_db():
    return MockDatabase()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# =====================================================================
# Live Weather Endpoint
# =====================================================================


def test_endpoint_city_weather_live_fallback_to_db(client):
    """GET /api/v1/cities/{city_id}/weather/live falls back cleanly to DB observations in test fixture."""
    res = client.get("/api/v1/cities/tokyo_jp/weather/live")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["city_id"] == "tokyo_jp"
    assert body["data"]["meta"]["status"] in [LiveStatus.FRESH.value, LiveStatus.DATABASE.value]
    assert body["data"]["weather"] is not None


def test_endpoint_city_weather_live_not_found(client):
    """GET /api/v1/cities/{city_id}/weather/live returns 404 for unknown city."""
    res = client.get("/api/v1/cities/non_existent_city_xyz/weather/live")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"


# =====================================================================
# Live Air Quality Endpoint
# =====================================================================


def test_endpoint_city_air_quality_live_fallback_to_db(client):
    """GET /api/v1/cities/{city_id}/air-quality/live falls back to DB observation when live key unconfigured."""
    res = client.get("/api/v1/cities/tokyo_jp/air-quality/live")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["city_id"] == "tokyo_jp"
    # When no key is configured in test, status is DATABASE
    assert body["data"]["meta"]["status"] == LiveStatus.DATABASE.value
    assert body["data"]["air_quality"]["pollutants"]["pm25"] == 12.5


# =====================================================================
# Currency Convert Endpoint
# =====================================================================


def test_endpoint_currency_convert_identity(client):
    """GET /api/v1/currency/convert converts identical currencies with 1.0 rate."""
    res = client.get("/api/v1/currency/convert?from_currency=USD&to_currency=USD&amount=250")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["from_currency"] == "USD"
    assert body["data"]["to_currency"] == "USD"
    assert body["data"]["conversion"]["rate"] == 1.0
    assert body["data"]["conversion"]["converted_amount"] == 250.0


# =====================================================================
# Geocoding Endpoints
# =====================================================================


def test_endpoint_geocoding_search_empty_query(client):
    """GET /api/v1/geocoding/search with empty query handled cleanly."""
    res = client.get("/api/v1/geocoding/search?q=%20")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["results"] == []


def test_endpoint_geocoding_reverse_valid_coords(client):
    """GET /api/v1/geocoding/reverse parameters validated."""
    res = client.get("/api/v1/geocoding/reverse?lat=19.0758&lon=72.8775")
    # Will call provider or return response structure
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "latitude" in body["data"]
    assert "longitude" in body["data"]


# =====================================================================
# Routes Endpoint
# =====================================================================


def test_endpoint_routes(client):
    """GET /api/v1/routes calculates route or reports unavailable cleanly."""
    res = client.get("/api/v1/routes?origin_lat=19.0758&origin_lon=72.8775&dest_lat=18.5204&dest_lon=73.8567")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "origin" in body["data"]
    assert "destination" in body["data"]
    assert "meta" in body["data"]


# =====================================================================
# Places Endpoint
# =====================================================================


def test_endpoint_places_unsupported_category(client):
    """GET /api/v1/places/search returns UNAVAILABLE status for unsupported category."""
    res = client.get("/api/v1/places/search?lat=19.0&lon=72.0&category=unsupported_amenity_xyz")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["meta"]["status"] == LiveStatus.UNAVAILABLE.value
    assert body["data"]["places"] == []


# =====================================================================
# Transit Endpoint
# =====================================================================


def test_endpoint_transit_unconfigured_city(client):
    """GET /api/v1/transit/{city_id} returns explicit UNAVAILABLE without claiming universal coverage."""
    res = client.get("/api/v1/transit/tokyo_jp")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["city_id"] == "tokyo_jp"
    assert body["data"]["meta"]["status"] == LiveStatus.UNAVAILABLE.value
    assert body["data"]["transit"]["is_feed_configured"] is False
    assert "Universal global coverage is not claimed" in body["data"]["meta"]["error_detail"]
