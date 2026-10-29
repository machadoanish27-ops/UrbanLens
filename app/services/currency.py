"""Currency exchange and conversion service layer."""

from datetime import datetime, timezone
from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.logging import get_logger
from app.data.currencies import COUNTRY_CURRENCY_REGISTRY, DEFAULT_CURRENCY, get_currency_for_country
from app.providers.currency.base import BaseCurrencyProvider
from app.providers.currency.exchangerate_api import ExchangeRateApiCurrencyProvider
from app.providers.currency.frankfurter import FrankfurterCurrencyProvider

logger = get_logger("services.currency")


class CurrencyService:
    """Service mediating currency conversions through replaceable exchange rate providers."""

    def __init__(
        self,
        database: Database | None = None,
        primary_provider: BaseCurrencyProvider | None = None,
        secondary_provider: BaseCurrencyProvider | None = None,
        provider: BaseCurrencyProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.primary_provider = primary_provider or provider or FrankfurterCurrencyProvider()
        self.secondary_provider = secondary_provider if secondary_provider is not None else (ExchangeRateApiCurrencyProvider() if provider is None else None)
        # Keep self.provider pointing to primary for backward compatibility
        self.provider = self.primary_provider
        self.cache = cache

    async def get_usd_benchmark(self, currency_code: str) -> dict[str, Any]:
        """Calculate relative USD benchmark rate without claiming USD is 'highest currency'."""
        clean = currency_code.strip().upper()
        if clean == "USD":
            return {
                "currency": "USD",
                "rate_to_usd": 1.0,
                "usd_to_currency": 1.0,
                "label": "USD benchmark",
            }

        # Attempt to get USD -> currency conversion
        try:
            res = await self.convert_currency("USD", clean, amount=1.0, include_benchmarks=False)
            rate = res.get("rate")
            if rate and rate > 0:
                rate_to_usd = round(1.0 / rate, 6)
                return {
                    "currency": clean,
                    "rate_to_usd": rate_to_usd,
                    "usd_to_currency": rate,
                    "label": "USD benchmark",
                }
        except Exception as exc:
            logger.debug("Failed to calculate USD benchmark for %s: %s", clean, exc)

        return {
            "currency": clean,
            "rate_to_usd": None,
            "usd_to_currency": None,
            "label": "USD benchmark",
        }

    async def convert_currency(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
        include_benchmarks: bool = True,
    ) -> dict[str, Any]:
        """Convert an amount from source currency to target currency using provider adapter.
        
        Strictly follows LIVE API -> recent cache -> explicit unavailable. Never fabricates rates.
        """
        clean_from = from_currency.strip().upper()
        clean_to = to_currency.strip().upper()

        if len(clean_from) != 3 or len(clean_to) != 3:
            return {
                "from_currency": clean_from,
                "to_currency": clean_to,
                "base_currency": clean_from,
                "quote_currency": clean_to,
                "amount": amount,
                "rate": None,
                "inverse_rate": None,
                "converted_amount": None,
                "provider": getattr(self.provider, "provider_name", "frankfurter"),
                "source": getattr(self.provider, "source_info", "https://api.frankfurter.dev"),
                "status": "unavailable",
                "observed_at": None,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": None,
                "usd_benchmark_base": None,
                "usd_benchmark_quote": None,
                "conversion": None,
                "meta": {
                    "provider": getattr(self.provider, "provider_name", "frankfurter"),
                    "status": "unavailable",
                    "error_detail": f"Invalid 3-letter currency code: '{from_currency}', '{to_currency}'.",
                },
            }

        cache_key = build_cache_key("currency", from_cur=clean_from, to_cur=clean_to, amount=amount)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached and cached.get("rate") is not None:
                cached_res = dict(cached)
                cached_res["status"] = "cached"
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True, "status": "cached"}
                return cached_res

        # 1. Query Primary Provider (Frankfurter / ECB)
        res = None
        active_provider = self.primary_provider
        try:
            res = await self.primary_provider.convert(
                from_currency=clean_from,
                to_currency=clean_to,
                amount=amount,
            )
        except Exception as exc:
            logger.warning("Primary currency provider exception for %s/%s: %s", clean_from, clean_to, exc)
            res = None

        # 2. Query Secondary Provider (ExchangeRate-API) if primary failed or does not support currency pair
        if (not res or not res.is_successful or not res.data) and self.secondary_provider:
            try:
                sec_res = await self.secondary_provider.convert(
                    from_currency=clean_from,
                    to_currency=clean_to,
                    amount=amount,
                )
                if sec_res:
                    res = sec_res
                    active_provider = self.secondary_provider
            except Exception as exc:
                logger.warning("Secondary currency provider exception for %s/%s: %s", clean_from, clean_to, exc)

        now_utc = datetime.now(timezone.utc).isoformat()

        if res and res.is_successful and res.data:
            rate = res.data.rate
            converted_amount = res.data.converted_amount
            inverse_rate = round(1.0 / rate, 6) if rate > 0 else None
            observed_at = str(res.meta.observed_at) if res.meta.observed_at else None

            # Calculate benchmarks if requested
            bench_base = None
            bench_quote = None
            if include_benchmarks:
                bench_base = await self.get_usd_benchmark(clean_from)
                bench_quote = await self.get_usd_benchmark(clean_to)

            result = {
                "from_currency": clean_from,
                "to_currency": clean_to,
                "base_currency": clean_from,
                "quote_currency": clean_to,
                "amount": amount,
                "rate": rate,
                "inverse_rate": inverse_rate,
                "converted_amount": converted_amount,
                "provider": res.meta.provider,
                "source": res.meta.source,
                "status": "fresh",
                "observed_at": observed_at,
                "fetched_at": res.meta.fetched_at,
                "last_updated": observed_at or now_utc,
                "usd_benchmark_base": bench_base,
                "usd_benchmark_quote": bench_quote,
                "conversion": res.data.model_dump(),
                "meta": res.meta.model_dump(),
            }

            if self.cache:
                self.cache.set(cache_key, result, ttl_seconds=600.0)

            return result

        # Fallback to general base pair cache (rate for amount=1)
        fallback_cache_key = build_cache_key("currency", from_cur=clean_from, to_cur=clean_to, amount=1.0)
        if self.cache:
            stale = self.cache.get(fallback_cache_key)
            if stale and stale.get("rate") is not None:
                stale_rate = stale["rate"]
                return {
                    "from_currency": clean_from,
                    "to_currency": clean_to,
                    "base_currency": clean_from,
                    "quote_currency": clean_to,
                    "amount": amount,
                    "rate": stale_rate,
                    "inverse_rate": round(1.0 / stale_rate, 6) if stale_rate > 0 else None,
                    "converted_amount": round(amount * stale_rate, 4),
                    "provider": stale.get("provider", "frankfurter"),
                    "source": stale.get("source", "https://api.frankfurter.dev"),
                    "status": "cached",
                    "observed_at": stale.get("observed_at"),
                    "fetched_at": now_utc,
                    "last_updated": stale.get("last_updated"),
                    "usd_benchmark_base": stale.get("usd_benchmark_base"),
                    "usd_benchmark_quote": stale.get("usd_benchmark_quote"),
                    "conversion": stale.get("conversion"),
                    "meta": {
                        "provider": stale.get("provider", "frankfurter"),
                        "status": "cached",
                        "cached": True,
                        "warning": "Live provider unavailable, returning recent cached rate.",
                    },
                }

        # Explicitly unavailable
        error_msg = res.meta.error_detail if res and res.meta else "Exchange rate provider currently unreachable."
        return {
            "from_currency": clean_from,
            "to_currency": clean_to,
            "base_currency": clean_from,
            "quote_currency": clean_to,
            "amount": amount,
            "rate": None,
            "inverse_rate": None,
            "converted_amount": None,
            "provider": getattr(active_provider, "provider_name", "currency_provider"),
            "source": getattr(active_provider, "source_info", "https://api.frankfurter.dev"),
            "status": "unavailable",
            "observed_at": None,
            "fetched_at": now_utc,
            "last_updated": None,
            "usd_benchmark_base": None,
            "usd_benchmark_quote": None,
            "conversion": None,
            "error_detail": error_msg,
            "meta": {
                "provider": getattr(active_provider, "provider_name", "currency_provider"),
                "status": "unavailable",
                "error_detail": error_msg,
            },
        }

    def get_supported_currencies(self) -> list[dict[str, str]]:
        """List distinct active currencies mapped to countries."""
        seen = set()
        currencies = []
        for item in COUNTRY_CURRENCY_REGISTRY.values():
            if item["code"] not in seen:
                seen.add(item["code"])
                currencies.append(item)
        currencies.sort(key=lambda x: x["code"])
        return currencies
