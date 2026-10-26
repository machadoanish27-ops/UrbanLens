"""Routing and navigation distance calculation endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.routing import RouteResponse
from app.services.routing import RoutingService

router = APIRouter(prefix="/routes", tags=["Routing"])


@router.get(
    "",
    response_model=ApiResponse[RouteResponse],
    summary="Calculate road routing distance and duration via OSRM",
)
async def calculate_route(
    origin_lat: float = Query(..., ge=-90.0, le=90.0, description="Origin latitude"),
    origin_lon: float = Query(..., ge=-180.0, le=180.0, description="Origin longitude"),
    dest_lat: float = Query(..., ge=-90.0, le=90.0, description="Destination latitude"),
    dest_lon: float = Query(..., ge=-180.0, le=180.0, description="Destination longitude"),
    profile: str = Query("driving", pattern="^(driving|walking|cycling)$", description="Routing mode"),
    database: Database = Depends(get_db),
) -> ApiResponse[RouteResponse]:
    """Calculate driving distance and estimated travel duration using Project OSRM."""
    service = RoutingService(database)
    data = await service.calculate_route(
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        dest_lat=dest_lat,
        dest_lon=dest_lon,
        profile=profile,
    )
    return ApiResponse(
        data=RouteResponse(**data),
        meta=ResponseMeta(source="Project OSRM Routing Engine"),
    )
