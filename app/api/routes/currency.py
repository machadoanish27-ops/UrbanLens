"""Currency conversion endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

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
    from_currency: str = Query("USD", min_length=3, max_length=3, description="Source 3-letter currency code (e.g. USD)"),
    to_currency: str = Query("EUR", min_length=3, max_length=3, description="Target 3-letter currency code (e.g. EUR)"),
    amount: float = Query(1.0, gt=0, description="Amount to convert"),
    database: Database = Depends(get_db),
) -> ApiResponse[CurrencyConversionResponse]:
    """Calculate currency conversion using Frankfurter live European Central Bank exchange rates."""
    service = CurrencyService(database)
    data = await service.convert_currency(
        from_currency=from_currency,
        to_currency=to_currency,
        amount=amount,
    )
    return ApiResponse(
        data=CurrencyConversionResponse(**data),
        meta=ResponseMeta(source="Frankfurter Currency Exchange API"),
    )
