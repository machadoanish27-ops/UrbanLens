"""Currency exchange and conversion service layer."""

from typing import Any
from pymongo.database import Database

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
    ) -> None:
        self.database = database
        self.provider = provider or FrankfurterCurrencyProvider()

    async def convert_currency(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
    ) -> dict[str, Any]:
        """Convert an amount from source currency to target currency using provider adapter."""
        res = await self.provider.convert(
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
        )

        return {
            "from_currency": from_currency.strip().upper(),
            "to_currency": to_currency.strip().upper(),
            "amount": amount,
            "conversion": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }
