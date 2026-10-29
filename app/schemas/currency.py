"""Currency conversion response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class UsdBenchmark(BaseModel):
    """Relative benchmark rate against USD (strictly labeled as benchmark, not highest currency)."""

    currency: str
    rate_to_usd: float | None = None  # 1 Currency = X USD
    usd_to_currency: float | None = None  # 1 USD = X Currency
    label: str = "USD benchmark"


class CurrencyConversionResponse(BaseModel):
    """Response payload for currency exchange rate conversion."""

    from_currency: str = Field(..., description="Base 3-letter currency code")
    to_currency: str = Field(..., description="Target 3-letter currency code")
    base_currency: str | None = None
    quote_currency: str | None = None
    amount: float = Field(default=1.0)
    rate: float | None = None
    inverse_rate: float | None = None
    converted_amount: float | None = None
    provider: str = "frankfurter"
    source: str = "https://api.frankfurter.dev"
    status: str = "fresh"  # fresh, cached, unavailable
    observed_at: str | None = None
    fetched_at: str | None = None
    last_updated: str | None = None
    usd_benchmark_base: UsdBenchmark | None = None
    usd_benchmark_quote: UsdBenchmark | None = None
    conversion: dict[str, Any] | None = None
    error_detail: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
