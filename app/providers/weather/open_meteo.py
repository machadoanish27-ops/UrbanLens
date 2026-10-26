"""Open-Meteo live weather provider implementation."""

from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.weather.base import (
    BaseWeatherProvider,
    NormalizedCurrentWeather,
    NormalizedDailyForecast,
    NormalizedWeather,
)

logger = get_logger("providers.weather.open_meteo")

WMO_CODE_MAP: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def describe_wmo_code(code: int | None) -> str | None:
    """Map WMO meteorological code to human-readable weather description."""
    if code is None:
        return None
    return WMO_CODE_MAP.get(code, f"Weather code {code}")


class OpenMeteoWeatherProvider(BaseWeatherProvider):
    """Live weather adapter backed by the Open-Meteo API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.OPEN_METEO_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "open-meteo"

    @property
    def source_info(self) -> str:
        return "https://open-meteo.com"

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> ProviderResponse[NormalizedWeather]:
        """Fetch current weather and daily forecasts from Open-Meteo."""
        # Clamp forecast horizon between 1 and 16 days
        horizon = max(1, min(16, forecast_days))
        endpoint = f"{self.base_url}/forecast"
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": horizon,
            "timezone": "auto",
        }

        try:
            if self._external_client:
                response = await self._external_client.get(endpoint, params=params, timeout=self.timeout)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(endpoint, params=params, timeout=self.timeout)

            if response.status_code != 200:
                logger.warning(
                    "Open-Meteo HTTP %d: %s",
                    response.status_code,
                    response.text[:200],
                )
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"Open-Meteo returned HTTP {response.status_code}",
                    ),
                    data=None,
                )

            payload = response.json()
            return self._normalize_response(latitude, longitude, payload)

        except httpx.TimeoutException:
            logger.warning("Open-Meteo request timed out for (%.4f, %.4f)", latitude, longitude)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail="Open-Meteo request timed out",
                ),
                data=None,
            )
        except Exception as exc:
            logger.error("Open-Meteo request error for (%.4f, %.4f): %s", latitude, longitude, str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Open-Meteo communication failure: {str(exc)}",
                ),
                data=None,
            )

    def _normalize_response(
        self,
        latitude: float,
        longitude: float,
        payload: dict[str, Any],
    ) -> ProviderResponse[NormalizedWeather]:
        """Normalize raw Open-Meteo JSON into UrbanLens standard weather model."""
        current_data = payload.get("current") or {}
        daily_data = payload.get("daily") or {}

        observed_at = current_data.get("time")
        weather_code = current_data.get("weather_code")

        current = NormalizedCurrentWeather(
            temperature_c=current_data.get("temperature_2m"),
            apparent_temperature_c=current_data.get("apparent_temperature"),
            relative_humidity_pct=current_data.get("relative_humidity_2m"),
            surface_pressure_mb=current_data.get("surface_pressure"),
            wind_speed_kph=current_data.get("wind_speed_10m"),
            precipitation_mm=current_data.get("precipitation"),
            weather_code=weather_code,
            condition=describe_wmo_code(weather_code),
            observed_at=str(observed_at) if observed_at else None,
        )

        daily_forecasts: list[NormalizedDailyForecast] = []
        dates = daily_data.get("time", [])
        min_temps = daily_data.get("temperature_2m_min", [])
        max_temps = daily_data.get("temperature_2m_max", [])
        precips = daily_data.get("precipitation_sum", [])
        codes = daily_data.get("weather_code", [])

        for idx, date_str in enumerate(dates):
            d_code = codes[idx] if idx < len(codes) else None
            daily_forecasts.append(
                NormalizedDailyForecast(
                    date=str(date_str),
                    temp_min_c=min_temps[idx] if idx < len(min_temps) else None,
                    temp_max_c=max_temps[idx] if idx < len(max_temps) else None,
                    precipitation_mm=precips[idx] if idx < len(precips) else None,
                    weather_code=d_code,
                    condition=describe_wmo_code(d_code),
                )
            )

        normalized = NormalizedWeather(
            latitude=payload.get("latitude", latitude),
            longitude=payload.get("longitude", longitude),
            timezone=payload.get("timezone"),
            elevation=payload.get("elevation"),
            current=current,
            daily_forecasts=daily_forecasts,
        )

        return ProviderResponse(
            meta=self.create_meta(
                status=LiveStatus.FRESH,
                observed_at=str(observed_at) if observed_at else None,
            ),
            data=normalized,
        )
