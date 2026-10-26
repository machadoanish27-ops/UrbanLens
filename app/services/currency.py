"""Currency exchange and conversion service layer."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.logging import get_logger
from app.providers.currency.base import BaseCurrencyProvider
from app.providers.currency.frankfurter import FrankfurterCurrencyProvider

logger = get_logger("services.currency")


class CurrencyService:
    """Service mediating currency conversions through replaceable exchange rate providers."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BaseCurrencyProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.provider = provider or FrankfurterCurrencyProvider()
        self.cache = cache

    async def convert_currency(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
    ) -> dict[str, Any]:
        """Convert an amount from source currency to target currency using provider adapter."""
        clean_from = from_currency.strip().upper()
        clean_to = to_currency.strip().upper()

        cache_key = build_cache_key("currency", from_cur=clean_from, to_cur=clean_to, amount=amount)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        res = await self.provider.convert(
            from_currency=clean_from,
            to_currency=clean_to,
            amount=amount,
        )

        result = {
            "from_currency": clean_from,
            "to_currency": clean_to,
            "amount": amount,
            "conversion": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=600.0)

        return result

