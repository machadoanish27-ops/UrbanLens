"""Places and points of interest endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.places import PlacesSearchResponse
from app.services.places import PlacesService

router = APIRouter(prefix="/places", tags=["Places"])


@router.get(
    "/search",
    response_model=ApiResponse[PlacesSearchResponse],
    summary="Search category-based POIs via OpenStreetMap Overpass",
)
async def search_places(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Center latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Center longitude"),
    category: str = Query("hospital", description="Amenity category (e.g. hospital, school, university, pharmacy, supermarket, park)"),
    radius: int = Query(1500, ge=200, le=5000, description="Search radius in meters (max 5000m)"),
    limit: int = Query(10, ge=1, le=25, description="Max items (max 25)"),
    database: Database = Depends(get_db),
) -> ApiResponse[PlacesSearchResponse]:
    """Perform bounded, category-based points of interest discovery using OpenStreetMap Overpass."""
    service = PlacesService(database)
    data = await service.search_places(
        latitude=lat,
        longitude=lon,
        category=category,
        radius=radius,
        limit=limit,
    )
    return ApiResponse(
        data=PlacesSearchResponse(**data),
        meta=ResponseMeta(source="OpenStreetMap Overpass API"),
    )
