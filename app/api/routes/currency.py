"""Currency conversion and registry endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.database import Database

from app.data.currencies import get_currency_for_country
from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.currency import CurrencyConversionResponse
from app.services.currency import CurrencyService

router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get(
    "/convert",
    response_model=ApiResponse[CurrencyConversionResponse],
    summary="Convert currency amounts using live ECB rates via Frankfurter",
)
async def convert_currency(
    from_currency: str | None = Query(None, description="Source 3-letter currency code (e.g. USD)"),
    to_currency: str | None = Query(None, description="Target 3-letter currency code (e.g. EUR)"),
    base: str | None = Query(None, description="Alias for from_currency"),
    quote: str | None = Query(None, description="Alias for to_currency"),
    amount: float = Query(1.0, gt=0, description="Amount to convert"),
    include_benchmarks: bool = Query(True, description="Include relative USD benchmark conversions"),
    database: Database = Depends(get_db),
) -> ApiResponse[CurrencyConversionResponse]:
    """Calculate currency conversion using Frankfurter live European Central Bank exchange rates."""
    src = (from_currency or base or "USD").strip().upper()
    dst = (to_currency or quote or "EUR").strip().upper()
    if len(src) != 3 or len(dst) != 3 or not src.isalpha() or not dst.isalpha():
        raise HTTPException(
            status_code=422,
            detail=f"Currency codes must be 3-letter ISO 4217 alphabetic codes. Received: '{src}', '{dst}'.",
        )

    service = CurrencyService(database)
    data = await service.convert_currency(
        from_currency=src,
        to_currency=dst,
        amount=amount,
        include_benchmarks=include_benchmarks,
    )
    return ApiResponse(
        data=CurrencyConversionResponse(**data),
        meta=ResponseMeta(source="Frankfurter Currency Exchange API"),
    )


@router.get(
    "/currencies",
    summary="Get list of supported world currencies with symbols and names",
)
def get_supported_currencies(
    database: Database = Depends(get_db),
) -> ApiResponse[list[dict[str, str]]]:
    """Retrieve all supported ISO 4217 currencies and symbols."""
    service = CurrencyService(database)
    items = service.get_supported_currencies()
    return ApiResponse(
        data=items,
        meta=ResponseMeta(source="ISO 4217 Currency Standards"),
    )


@router.get(
    "/lookup/{country_iso2}",
    summary="Look up national currency for country ISO-2 code",
)
def lookup_country_currency(
    country_iso2: str,
) -> ApiResponse[dict[str, str]]:
    """Retrieve currency code, symbol, and name for country ISO2 code."""
    res = get_currency_for_country(country_iso2)
    return ApiResponse(
        data=res,
        meta=ResponseMeta(source="ISO 3166 / ISO 4217 Currency Registry"),
    )
