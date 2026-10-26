"""Geocoding search and reverse lookup endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.geocoding import GeocodingReverseResponse, GeocodingSearchResponse
from app.services.geocoding import GeocodingService

router = APIRouter(prefix="/geocoding", tags=["Geocoding"])


@router.get(
    "/search",
    response_model=ApiResponse[GeocodingSearchResponse],
    summary="Forward geocode location query via Nominatim",
)
async def search_geocoding(
    q: str = Query(..., min_length=1, description="Place or address query string"),
    limit: int = Query(5, ge=1, le=20, description="Max results"),
    database: Database = Depends(get_db),
) -> ApiResponse[GeocodingSearchResponse]:
    """Forward geocode a text address or city query with Nominatim."""
    service = GeocodingService(database)
    data = await service.search(query=q, limit=limit)
    return ApiResponse(
        data=GeocodingSearchResponse(**data),
        meta=ResponseMeta(source="OpenStreetMap Nominatim Geocoder"),
    )


@router.get(
    "/reverse",
    response_model=ApiResponse[GeocodingReverseResponse],
    summary="Reverse geocode coordinates via Nominatim",
)
async def reverse_geocoding(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude"),
    database: Database = Depends(get_db),
) -> ApiResponse[GeocodingReverseResponse]:
    """Reverse geocode geographic coordinates to location address description."""
    service = GeocodingService(database)
    data = await service.reverse(latitude=lat, longitude=lon)
    return ApiResponse(
        data=GeocodingReverseResponse(**data),
        meta=ResponseMeta(source="OpenStreetMap Nominatim Reverse Geocoder"),
    )
