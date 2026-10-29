"""ExchangeRate-API open access currency conversion provider implementation."""

from datetime import datetime, timezone
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.currency.base import (
    BaseCurrencyProvider,
    NormalizedCurrencyConversion,
)

logger = get_logger("providers.currency.exchangerate_api")


class ExchangeRateApiCurrencyProvider(BaseCurrencyProvider):
    """Secondary live exchange rate provider backed by ExchangeRate-API open access tier (160+ world currencies)."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or getattr(settings, "EXCHANGERATE_API_BASE_URL", "https://open.er-api.com/v6")).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "exchangerate_api"

    @property
    def source_info(self) -> str:
        return "https://open.er-api.com"

    async def convert(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
    ) -> ProviderResponse[NormalizedCurrencyConversion]:
        """Convert currency using ExchangeRate-API open tier."""
        source = from_currency.strip().upper()
        target = to_currency.strip().upper()

        if len(source) != 3 or len(target) != 3:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail=f"Invalid ISO 4217 currency code format: '{from_currency}', '{to_currency}'.",
                ),
                data=None,
            )

        # Identity conversion
        if source == target:
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH, observed_at=today_str),
                data=NormalizedCurrencyConversion(
                    from_currency=source,
                    to_currency=target,
                    amount=amount,
                    rate=1.0,
                    converted_amount=amount,
                    date=today_str,
                ),
            )

        endpoint = f"{self.base_url}/latest/{source}"

        try:
            if self._external_client:
                response = await self._external_client.get(endpoint, timeout=self.timeout)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(endpoint, timeout=self.timeout)

            if response.status_code == 404:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"Base currency '{source}' not supported by ExchangeRate-API.",
                    ),
                    data=None,
                )

            if response.status_code != 200:
                logger.warning("ExchangeRate-API HTTP %d: %s", response.status_code, response.text[:200])
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"ExchangeRate-API error (HTTP {response.status_code}).",
                    ),
                    data=None,
                )

            payload = response.json()
            if payload.get("result") != "success":
                err = payload.get("error-type") or "Unknown error"
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"ExchangeRate-API query failed: {err}.",
                    ),
                    data=None,
                )

            rates = payload.get("rates") or {}
            rate = rates.get(target)

            if rate is None:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"Target currency '{target}' not present in ExchangeRate-API rates for base '{source}'.",
                    ),
                    data=None,
                )

            rate_float = float(rate)
            converted = round(amount * rate_float, 4)
            unit_rate = round(rate_float, 6)

            # Extract date string
            date_raw = payload.get("time_last_update_utc")
            if date_raw:
                try:
                    # e.g. "Thu, 29 Oct 2026 00:02:31 +0000"
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(date_raw)
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            normalized = NormalizedCurrencyConversion(
                from_currency=source,
                to_currency=target,
                amount=amount,
                rate=unit_rate,
                converted_amount=converted,
                date=date_str,
            )

            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.FRESH,
                    observed_at=date_str,
                ),
                data=normalized,
            )

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning("ExchangeRate-API connection failure for %s/%s: %s", source, target, exc)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail=f"ExchangeRate-API network error: {str(exc)}",
                ),
                data=None,
            )
        except Exception as exc:
            logger.error("Unexpected error in ExchangeRate-API provider: %s", exc)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Internal conversion error: {str(exc)}",
                ),
                data=None,
            )
