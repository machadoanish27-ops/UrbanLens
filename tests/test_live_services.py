"""Unit tests for service layer live provider integration and fallback architecture."""

import asyncio
import pytest

from app.core.exceptions import ResourceNotFoundException
from app.providers.base import LiveMetadata, LiveStatus, ProviderResponse
from app.providers.weather.base import (
    BaseWeatherProvider,
    NormalizedCurrentWeather,
    NormalizedWeather,
)
from app.providers.air_quality.base import (
    BaseAirQualityProvider,
    NormalizedAirQuality,
    NormalizedPollutants,
)
from app.providers.currency.base import (
    BaseCurrencyProvider,
    NormalizedCurrencyConversion,
)
from app.providers.transit.base import (
    BaseTransitProvider,
    NormalizedTransitFeedInfo,
)
from app.services.air_quality import AirQualityService
from app.services.currency import CurrencyService
from app.services.transit import TransitService
from app.services.weather import WeatherService
from tests.conftest import MockDatabase


# Mock Weather Provider
class MockWeatherProvider(BaseWeatherProvider):
    def __init__(self, succeed: bool = True, error_detail: str = "Provider down") -> None:
        self.succeed = succeed
        self.error_detail = error_detail

    @property
    def provider_name(self) -> str:
        return "mock-weather"

    @property
    def source_info(self) -> str:
        return "https://mock-weather.test"

    async def get_weather(self, latitude: float, longitude: float, forecast_days: int = 7):
        if self.succeed:
            current = NormalizedCurrentWeather(
                temperature_c=25.0,
                apparent_temperature_c=26.0,
                relative_humidity_pct=50.0,
                surface_pressure_mb=1012.0,
                wind_speed_kph=10.0,
                precipitation_mm=0.0,
                weather_code=0,
                condition="Clear sky",
                observed_at="2026-10-27T01:00:00Z",
            )
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH, observed_at="2026-10-27T01:00:00Z"),
                data=NormalizedWeather(
                    latitude=latitude,
                    longitude=longitude,
                    current=current,
                    daily_forecasts=[],
                ),
            )
        return ProviderResponse(
            meta=self.create_meta(status=LiveStatus.ERROR, error_detail=self.error_detail),
            data=None,
        )


# Mock Air Quality Provider
class MockAirQualityProvider(BaseAirQualityProvider):
    def __init__(self, succeed: bool = True, error_detail: str = "AQ provider down") -> None:
        self.succeed = succeed
        self.error_detail = error_detail

    @property
    def provider_name(self) -> str:
        return "mock-openaq"

    @property
    def source_info(self) -> str:
        return "https://mock-openaq.test"

    async def get_air_quality(self, latitude: float, longitude: float, radius: int = 25000):
        if self.succeed:
            pollutants = NormalizedPollutants(pm25=12.5, pm10=25.0, no2=18.0)
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH, observed_at="2026-10-27T01:15:00Z"),
                data=NormalizedAirQuality(
                    latitude=latitude,
                    longitude=longitude,
                    location_name="Mock Central Station",
                    observed_at="2026-10-27T01:15:00Z",
                    pollutants=pollutants,
                    available_pollutants=["pm25", "pm10", "no2"],
                ),
            )
        return ProviderResponse(
            meta=self.create_meta(status=LiveStatus.UNAVAILABLE, error_detail=self.error_detail),
            data=None,
        )


# =====================================================================
# WeatherService Tests
# =====================================================================


def test_weather_service_live_success():
    """Verify WeatherService returns FRESH status when live provider succeeds."""
    async def run():
        db = MockDatabase()
        service = WeatherService(db, provider=MockWeatherProvider(succeed=True))
        res = await service.get_live_weather("tokyo_jp")

        assert res["city_id"] == "tokyo_jp"
        assert res["meta"]["status"] == LiveStatus.FRESH
        assert res["meta"]["provider"] == "mock-weather"
        assert res["weather"]["current"]["temperature_c"] == 25.0

    asyncio.run(run())


def test_weather_service_fallback_to_database():
    """Verify WeatherService falls back to MongoDB ground-truth observations when live provider fails."""
    async def run():
        db = MockDatabase()
        service = WeatherService(db, provider=MockWeatherProvider(succeed=False, error_detail="Open-Meteo timeout"))
        res = await service.get_live_weather("tokyo_jp")

        assert res["city_id"] == "tokyo_jp"
        # Status MUST be DATABASE, not FRESH! Stale data is never labeled live
        assert res["meta"]["status"] == LiveStatus.DATABASE
        assert res["meta"]["provider"] == "mongodb"
        assert "fallback" in res["meta"]["error_detail"].lower()
        assert res["weather"] is not None
        # Tokyo mock DB fixture has temperature_c = 19.5
        assert res["weather"]["current"]["temperature_c"] == 19.5

    asyncio.run(run())


def test_weather_service_city_not_found():
    """Verify WeatherService raises ResourceNotFoundException for non-existent city."""
    async def run():
        db = MockDatabase()
        service = WeatherService(db, provider=MockWeatherProvider())
        with pytest.raises(ResourceNotFoundException):
            await service.get_live_weather("city_non_existent")

    asyncio.run(run())


def test_weather_service_fallback_when_db_also_empty():
    """Verify WeatherService returns UNAVAILABLE when live provider fails and DB has no observations."""
    async def run():
        db = MockDatabase()
        # Add city with no weather observations
        db.collections["cities"].documents.append({
            "city_id": "empty_city",
            "name": "Empty City",
            "latitude": 10.0,
            "longitude": 20.0,
        })
        service = WeatherService(db, provider=MockWeatherProvider(succeed=False))
        res = await service.get_live_weather("empty_city")

        assert res["meta"]["status"] == LiveStatus.UNAVAILABLE
        assert res["weather"] is None

    asyncio.run(run())


# =====================================================================
# AirQualityService Tests
# =====================================================================


def test_air_quality_service_live_success():
    """Verify AirQualityService returns FRESH status when live provider succeeds."""
    async def run():
        db = MockDatabase()
        service = AirQualityService(db, provider=MockAirQualityProvider(succeed=True))
        res = await service.get_live_air_quality("tokyo_jp")

        assert res["city_id"] == "tokyo_jp"
        assert res["meta"]["status"] == LiveStatus.FRESH
        assert res["air_quality"]["pollutants"]["pm25"] == 12.5

    asyncio.run(run())


def test_air_quality_service_fallback_to_global_weather_db():
    """Verify AirQualityService falls back to MongoDB Global Weather observations on live failure."""
    async def run():
        db = MockDatabase()
        service = AirQualityService(db, provider=MockAirQualityProvider(succeed=False, error_detail="OpenAQ rate limit"))
        res = await service.get_live_air_quality("tokyo_jp")

        assert res["city_id"] == "tokyo_jp"
        assert res["meta"]["status"] == LiveStatus.DATABASE
        assert res["air_quality"]["location_name"] == "MongoDB Ground-Truth Observation"
        # Tokyo mock fixture has pm25 = 12.5
        assert res["air_quality"]["pollutants"]["pm25"] == 12.5

    asyncio.run(run())


def test_air_quality_service_fallback_to_who_annual():
    """Verify AirQualityService falls back to WHO annual mean when Global Weather observation is absent."""
    async def run():
        db = MockDatabase()
        # Add city with only WHO observation
        db.collections["cities"].documents.append({
            "city_id": "who_only_city",
            "name": "WHO City",
            "latitude": 35.0,
            "longitude": 139.0,
        })
        db.collections["air_quality_observations_who"] = MockDatabase().collections.get("air_quality_observations_who") or None
        # Add WHO doc
        from tests.conftest import MockCollection
        db.collections["air_quality_observations_who"] = MockCollection("air_quality_observations_who", [
            {
                "city_id": "who_only_city",
                "source": "WHO",
                "year": 2022,
                "pm25_annual_mean_ug_m3": 9.8,
                "pm10_annual_mean_ug_m3": 18.2,
            }
        ])
        service = AirQualityService(db, provider=MockAirQualityProvider(succeed=False))
        res = await service.get_live_air_quality("who_only_city")

        assert res["meta"]["status"] == LiveStatus.DATABASE
        assert "WHO Annual" in res["air_quality"]["location_name"]
        assert res["air_quality"]["pollutants"]["pm25"] == 9.8

    asyncio.run(run())


# =====================================================================
# CurrencyService Tests
# =====================================================================


def test_currency_service_convert():
    """Verify CurrencyService delegates to currency provider and preserves metadata."""
    class MockCurrencyProvider(BaseCurrencyProvider):
        @property
        def provider_name(self) -> str:
            return "mock-currency"
        @property
        def source_info(self) -> str:
            return "https://mock-currency.test"
        async def convert(self, from_currency: str, to_currency: str, amount: float = 1.0):
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH, observed_at="2026-10-26"),
                data=NormalizedCurrencyConversion(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=amount,
                    rate=0.85,
                    converted_amount=amount * 0.85,
                    date="2026-10-26",
                ),
            )

    async def run():
        service = CurrencyService(provider=MockCurrencyProvider())
        res = await service.convert_currency("USD", "EUR", amount=10.0)

        assert res["from_currency"] == "USD"
        assert res["to_currency"] == "EUR"
        assert res["conversion"]["converted_amount"] == 8.5
        assert res["meta"]["status"] == LiveStatus.FRESH

    asyncio.run(run())


# =====================================================================
# TransitService Tests
# =====================================================================


def test_transit_service_unconfigured():
    """Verify TransitService returns explicit DATA_UNAVAILABLE for unconfigured cities."""
    async def run():
        db = MockDatabase()
        service = TransitService(db)
        res = await service.get_transit_info("tokyo_jp")

        assert res["city_id"] == "tokyo_jp"
        assert res["meta"]["status"] == LiveStatus.UNAVAILABLE
        assert res["transit"]["is_feed_configured"] is False

    asyncio.run(run())
