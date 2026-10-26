"""Currency conversion response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class CurrencyConversionResponse(BaseModel):
    """Response payload for currency exchange rate conversion."""

    from_currency: str
    to_currency: str
    amount: float
    conversion: dict[str, Any] | None = None
    meta: dict[str, Any]
