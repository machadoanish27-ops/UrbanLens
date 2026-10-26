"""Frankfurter currency conversion provider implementation."""

from datetime import datetime, timezone
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.currency.base import (
    BaseCurrencyProvider,
    NormalizedCurrencyConversion,
)

logger = get_logger("providers.currency.frankfurter")


class FrankfurterCurrencyProvider(BaseCurrencyProvider):
    """Live exchange rate provider backed by Frankfurter API (European Central Bank rates)."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.FRANKFURTER_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "frankfurter"

    @property
    def source_info(self) -> str:
        return "https://api.frankfurter.dev"

    async def convert(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
    ) -> ProviderResponse[NormalizedCurrencyConversion]:
        """Convert currency using Frankfurter live exchange rates."""
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

        endpoint = f"{self.base_url}/latest"
        params = {
            "from": source,
            "to": target,
            "amount": amount,
        }

        try:
            if self._external_client:
                response = await self._external_client.get(endpoint, params=params, timeout=self.timeout)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(endpoint, params=params, timeout=self.timeout)

            if response.status_code == 404:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"Exchange rate not found for currency pair {source}/{target}.",
                    ),
                    data=None,
                )

            if response.status_code != 200:
                logger.warning("Frankfurter HTTP %d: %s", response.status_code, response.text[:200])
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"Frankfurter API error (HTTP {response.status_code}).",
                    ),
                    data=None,
                )

            payload = response.json()
            rates = payload.get("rates") or {}
            rate = rates.get(target)

            if rate is None:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"Target currency '{target}' not present in provider response.",
                    ),
                    data=None,
                )

            rate_float = float(rate)
            # If API converted using 'amount', converted_amount = rate; otherwise calculate
            converted = round(rate_float, 4) if payload.get("amount") == amount else round(amount * rate_float, 4)
            unit_rate = round(converted / amount, 6) if amount > 0 else rate_float
            date_str = str(payload.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d"))

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

        except httpx.TimeoutException:
            logger.warning("Frankfurter request timed out for %s -> %s", source, target)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail="Frankfurter currency provider request timed out.",
                ),
                data=None,
            )
        except Exception as exc:
            logger.error("Frankfurter error for %s -> %s: %s", source, target, str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Frankfurter currency communication error: {str(exc)}",
                ),
                data=None,
            )
