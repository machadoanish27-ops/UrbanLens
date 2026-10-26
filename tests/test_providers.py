"""Unit tests for live intelligence provider adapters using mocked HTTP calls."""

import asyncio
import pytest
import httpx

from app.providers.base import LiveStatus
from app.providers.weather import (
    NormalizedCurrentWeather,
    NormalizedWeather,
    OpenMeteoWeatherProvider,
)
from app.providers.air_quality import (
    NormalizedAirQuality,
    OpenAQAirQualityProvider,
)
from app.providers.currency import (
    FrankfurterCurrencyProvider,
    NormalizedCurrencyConversion,
)
from app.providers.geocoding import (
    NominatimGeocodingProvider,
    NormalizedGeocodingItem,
)
from app.providers.routing import (
    NormalizedRoute,
    OSRMRoutingProvider,
)
from app.providers.places import (
    NormalizedPlaceItem,
    OverpassPlacesProvider,
)
from app.providers.transit import (
    GTFSTransitProvider,
    NormalizedTransitFeedInfo,
)


# =====================================================================
# Weather: Open-Meteo
# =====================================================================


def test_open_meteo_success():
    """Verify Open-Meteo success and normalization of current weather and daily forecasts."""
    async def run():
        mock_payload = {
            "latitude": 19.08,
            "longitude": 72.88,
            "timezone": "Asia/Kolkata",
            "elevation": 8.0,
            "current": {
                "time": "2026-10-27T01:30",
                "temperature_2m": 28.5,
                "apparent_temperature": 30.2,
                "relative_humidity_2m": 55,
                "surface_pressure": 1010.5,
                "wind_speed_10m": 7.2,
                "precipitation": 0.0,
                "weather_code": 1,
            },
            "daily": {
                "time": ["2026-10-27", "2026-10-28"],
                "temperature_2m_min": [24.0, 24.5],
                "temperature_2m_max": [33.0, 32.5],
                "precipitation_sum": [0.0, 0.2],
                "weather_code": [1, 2],
            },
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenMeteoWeatherProvider(client=client)
            res = await provider.get_weather(latitude=19.0758, longitude=72.8775, forecast_days=2)

        assert res.meta.status == LiveStatus.FRESH
        assert res.meta.provider == "open-meteo"
        assert res.meta.source == "https://open-meteo.com"
        assert res.meta.observed_at == "2026-10-27T01:30"
        assert res.meta.fetched_at is not None
        assert res.meta.confidence is None

        assert res.data is not None
        assert res.data.current.temperature_c == 28.5
        assert res.data.current.condition == "Mainly clear"
        assert len(res.data.daily_forecasts) == 2
        assert res.data.daily_forecasts[0].date == "2026-10-27"
        assert res.data.daily_forecasts[0].temp_max_c == 33.0

    asyncio.run(run())


def test_open_meteo_timeout():
    """Verify graceful handling when Open-Meteo times out."""
    async def run():
        def timeout_handler(req):
            raise httpx.ReadTimeout("Connection timed out")

        transport = httpx.MockTransport(timeout_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenMeteoWeatherProvider(client=client)
            res = await provider.get_weather(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.ERROR
        assert "timed out" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


def test_open_meteo_http_500():
    """Verify graceful error reporting when Open-Meteo returns 500."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(500, text="Internal Server Error"))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenMeteoWeatherProvider(client=client)
            res = await provider.get_weather(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.ERROR
        assert "HTTP 500" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


# =====================================================================
# Air Quality: OpenAQ
# =====================================================================


def test_openaq_missing_api_key():
    """Verify OpenAQ gracefully returns UNAVAILABLE when API key is missing without raising."""
    async def run():
        provider = OpenAQAirQualityProvider(api_key=None)
        res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "OPENAQ_API_KEY" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


def test_openaq_http_401():
    """Verify OpenAQ gracefully returns UNAVAILABLE on 401 Unauthorized without exposing secret."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(401, json={"message": "Unauthorized"}))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenAQAirQualityProvider(api_key="invalid_test_key", client=client)
            res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "unauthorized" in res.meta.error_detail.lower()
        assert "invalid_test_key" not in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


def test_openaq_http_429():
    """Verify OpenAQ handles 429 rate limit gracefully."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(429, json={"message": "Rate limit"}))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenAQAirQualityProvider(api_key="test_key", client=client)
            res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "rate limit" in res.meta.error_detail.lower()
        assert res.data is None

    asyncio.run(run())


def test_openaq_http_500():
    """Verify OpenAQ handles 500 server error gracefully."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(500, text="Server Error"))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenAQAirQualityProvider(api_key="test_key", client=client)
            res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.ERROR
        assert "500" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


def test_openaq_timeout():
    """Verify OpenAQ handles network timeout gracefully."""
    async def run():
        def timeout_handler(req):
            raise httpx.ReadTimeout("Timeout")

        transport = httpx.MockTransport(timeout_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenAQAirQualityProvider(api_key="test_key", client=client)
            res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.ERROR
        assert "timed out" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


def test_openaq_success_pollutants_normalization():
    """Verify OpenAQ parses available pollutants, leaves unavailable pollutants null, and preserves timestamps."""
    async def run():
        mock_payload = {
            "results": [
                {
                    "id": 1042,
                    "name": "Bandra Kurla Complex AQMS",
                    "locality": "Mumbai",
                    "distance": 4200.0,
                    "sensors": [
                        {
                            "id": 1,
                            "parameter": {"name": "pm25", "units": "µg/m³"},
                            "latest": {"value": 45.8, "datetime": "2026-10-27T00:30:00Z"},
                        },
                        {
                            "id": 2,
                            "parameter": {"name": "pm10", "units": "µg/m³"},
                            "latest": {"value": 92.1, "datetime": "2026-10-27T00:30:00Z"},
                        },
                        {
                            "id": 3,
                            "parameter": {"name": "no2", "units": "ppm"},
                            "latest": {"value": 24.3, "datetime": "2026-10-27T00:15:00Z"},
                        },
                    ],
                }
            ]
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenAQAirQualityProvider(api_key="valid_key", client=client)
            res = await provider.get_air_quality(latitude=19.0758, longitude=72.8775)

        assert res.meta.status == LiveStatus.FRESH
        assert res.meta.provider == "openaq"
        assert res.meta.observed_at == "2026-10-27T00:30:00Z"

        assert res.data is not None
        assert res.data.location_name == "Bandra Kurla Complex AQMS"
        assert res.data.pollutants.pm25 == 45.8
        assert res.data.pollutants.pm10 == 92.1
        assert res.data.pollutants.no2 == 24.3
        assert res.data.pollutants.o3 is None
        assert res.data.pollutants.so2 is None
        assert res.data.pollutants.co is None
        assert set(res.data.available_pollutants) == {"pm25", "pm10", "no2"}

    asyncio.run(run())


# =====================================================================
# Currency: Frankfurter
# =====================================================================


def test_frankfurter_identity_conversion():
    """Verify converting currency to itself requires no network call and returns 1.0 rate."""
    async def run():
        provider = FrankfurterCurrencyProvider()
        res = await provider.convert(from_currency="USD", to_currency="USD", amount=50.0)

        assert res.meta.status == LiveStatus.FRESH
        assert res.data is not None
        assert res.data.rate == 1.0
        assert res.data.converted_amount == 50.0

    asyncio.run(run())


def test_frankfurter_success():
    """Verify live currency conversion using Frankfurter rates."""
    async def run():
        mock_payload = {
            "amount": 100.0,
            "base": "USD",
            "date": "2026-10-26",
            "rates": {"EUR": 89.38},
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = FrankfurterCurrencyProvider(client=client)
            res = await provider.convert(from_currency="USD", to_currency="EUR", amount=100.0)

        assert res.meta.status == LiveStatus.FRESH
        assert res.meta.provider == "frankfurter"
        assert res.meta.observed_at == "2026-10-26"
        assert res.data is not None
        assert res.data.from_currency == "USD"
        assert res.data.to_currency == "EUR"
        assert res.data.converted_amount == 89.38
        assert res.data.rate == round(89.38 / 100.0, 6)

    asyncio.run(run())


def test_frankfurter_unsupported_currency():
    """Verify Frankfurter 404 returns explicit UNAVAILABLE."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(404, json={"message": "not found"}))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = FrankfurterCurrencyProvider(client=client)
            res = await provider.convert(from_currency="XYZ", to_currency="EUR")

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert res.data is None

    asyncio.run(run())


def test_frankfurter_timeout():
    """Verify Frankfurter timeout returns ERROR."""
    async def run():
        def timeout_handler(req):
            raise httpx.ReadTimeout("Timeout")

        transport = httpx.MockTransport(timeout_handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = FrankfurterCurrencyProvider(client=client)
            res = await provider.convert(from_currency="USD", to_currency="JPY")

        assert res.meta.status == LiveStatus.ERROR
        assert "timed out" in res.meta.error_detail

    asyncio.run(run())


# =====================================================================
# Geocoding: Nominatim
# =====================================================================


def test_nominatim_forward_search_success():
    """Verify Nominatim forward geocoding normalization."""
    async def run():
        mock_results = [
            {
                "place_id": 12345,
                "name": "Mumbai",
                "display_name": "Mumbai, Maharashtra, India",
                "lat": "19.0758",
                "lon": "72.8775",
                "type": "city",
                "category": "place",
                "importance": 0.85,
                "boundingbox": ["18.89", "19.27", "72.77", "72.98"],
            }
        ]

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_results))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = NominatimGeocodingProvider(client=client)
            res = await provider.search(query="Mumbai")

        assert res.meta.status == LiveStatus.FRESH
        assert len(res.data) == 1
        assert res.data[0].name == "Mumbai"
        assert res.data[0].latitude == 19.0758
        assert res.data[0].longitude == 72.8775

    asyncio.run(run())


def test_nominatim_rate_limit_429():
    """Verify Nominatim 429 returns UNAVAILABLE."""
    async def run():
        transport = httpx.MockTransport(lambda req: httpx.Response(429, text="Too Many Requests"))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = NominatimGeocodingProvider(client=client)
            res = await provider.search(query="Tokyo")

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "rate limit" in res.meta.error_detail.lower()
        assert res.data == []

    asyncio.run(run())


def test_nominatim_reverse_geocoding():
    """Verify Nominatim reverse geocoding parses coordinates into address."""
    async def run():
        mock_payload = {
            "place_id": 9988,
            "name": "Nariman Point",
            "display_name": "Nariman Point, Mumbai, India",
            "lat": "18.9256",
            "lon": "72.8242",
            "type": "neighbourhood",
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = NominatimGeocodingProvider(client=client)
            res = await provider.reverse(latitude=18.9256, longitude=72.8242)

        assert res.meta.status == LiveStatus.FRESH
        assert res.data.name == "Nariman Point"

    asyncio.run(run())


# =====================================================================
# Routing: OSRM
# =====================================================================


def test_osrm_routing_success():
    """Verify OSRM calculates route distance and duration cleanly."""
    async def run():
        mock_payload = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 145200.0,
                    "duration": 7200.0,
                }
            ],
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OSRMRoutingProvider(client=client)
            res = await provider.get_route(
                origin_lat=19.0758, origin_lon=72.8775,
                dest_lat=18.5204, dest_lon=73.8567,
            )

        assert res.meta.status == LiveStatus.FRESH
        assert res.data is not None
        assert res.data.distance_meters == 145200.0
        assert res.data.distance_km == 145.2
        assert res.data.duration_seconds == 7200.0
        assert res.data.duration_minutes == 120.0

    asyncio.run(run())


def test_osrm_no_route():
    """Verify OSRM returns explicit UNAVAILABLE when waypoints cannot be connected."""
    async def run():
        mock_payload = {"code": "NoRoute", "message": "Impossible route"}
        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OSRMRoutingProvider(client=client)
            res = await provider.get_route(0.0, 0.0, 10.0, 10.0)

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "NoRoute" in res.meta.error_detail
        assert res.data is None

    asyncio.run(run())


# =====================================================================
# Places: Overpass
# =====================================================================


def test_overpass_places_success():
    """Verify Overpass bounded POI search normalizes coordinates and distance."""
    async def run():
        mock_payload = {
            "elements": [
                {
                    "type": "node",
                    "id": 101,
                    "lat": 19.0760,
                    "lon": 72.8780,
                    "tags": {"name": "Lilavati Hospital", "amenity": "hospital"},
                },
                {
                    "type": "way",
                    "id": 202,
                    "center": {"lat": 19.0770, "lon": 72.8790},
                    "tags": {"name": "Asian Heart Institute", "amenity": "hospital"},
                },
            ]
        }

        transport = httpx.MockTransport(lambda req: httpx.Response(200, json=mock_payload))
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OverpassPlacesProvider(client=client)
            res = await provider.get_places(latitude=19.0758, longitude=72.8775, category="hospital", radius=1000)

        assert res.meta.status == LiveStatus.FRESH
        assert len(res.data) == 2
        assert res.data[0].name == "Lilavati Hospital"
        assert res.data[0].distance_meters is not None
        assert res.data[0].distance_meters > 0

    asyncio.run(run())


def test_overpass_invalid_category():
    """Verify Overpass rejects unapproved arbitrary categories to prevent broad injection."""
    async def run():
        provider = OverpassPlacesProvider()
        res = await provider.get_places(latitude=19.0, longitude=72.0, category="arbitrary_unsupported")

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "not supported" in res.meta.error_detail
        assert res.data == []

    asyncio.run(run())


# =====================================================================
# Transit: GTFS Abstraction
# =====================================================================


def test_gtfs_unconfigured_city():
    """Verify unconfigured city returns explicit DATA_UNAVAILABLE without claiming universal coverage."""
    async def run():
        provider = GTFSTransitProvider(configured_feeds={})
        res = await provider.get_transit_info("city_1356226629")

        assert res.meta.status == LiveStatus.UNAVAILABLE
        assert "No GTFS transit feed is configured" in res.meta.error_detail
        assert "Universal global coverage is not claimed" in res.meta.error_detail
        assert res.data is not None
        assert res.data.is_feed_configured is False

    asyncio.run(run())


def test_gtfs_configured_city():
    """Verify configured city returns registered agency feed and alert notices."""
    async def run():
        feeds = {
            "city_tokyo": {
                "agency_name": "Tokyo Metro",
                "feed_url": "https://tokyometro.jp/gtfs.zip",
                "realtime_url": "https://tokyometro.jp/gtfs-rt",
                "routes_count": 9,
                "alerts": [
                    {
                        "id": "A1",
                        "cause": "MAINTENANCE",
                        "header_text": "Ginza Line scheduled maintenance",
                    }
                ],
            }
        }
        provider = GTFSTransitProvider(configured_feeds=feeds)
        res = await provider.get_transit_info("city_tokyo")

        assert res.meta.status == LiveStatus.FRESH
        assert res.data.agency_name == "Tokyo Metro"
        assert res.data.is_feed_configured is True
        assert len(res.data.alerts) == 1
        assert res.data.alerts[0].header_text == "Ginza Line scheduled maintenance"

    asyncio.run(run())
