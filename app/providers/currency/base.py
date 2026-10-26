"""Currency conversion provider base interface and schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedCurrencyConversion(BaseModel):
    """Normalized currency conversion result."""

    from_currency: str = Field(..., description="Source 3-letter currency code, e.g. USD")
    to_currency: str = Field(..., description="Target 3-letter currency code, e.g. EUR")
    amount: float = Field(default=1.0, description="Base amount converted")
    rate: float = Field(..., description="Exchange rate from source to target")
    converted_amount: float = Field(..., description="Calculated converted value")
    date: str = Field(..., description="Rate reference date from provider (YYYY-MM-DD)")


class BaseCurrencyProvider(BaseProvider):
    """Abstract interface for currency exchange rate providers."""

    @abstractmethod
    async def convert(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1.0,
    ) -> ProviderResponse[NormalizedCurrencyConversion]:
        """Convert an amount from source currency to target currency."""
        ...
