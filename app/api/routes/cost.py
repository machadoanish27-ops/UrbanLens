"""Cost of living endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.cost import CityCostOfLivingResponse, CostOfLivingMetricItem
from app.services.cost import CostOfLivingService

router = APIRouter(prefix="/cities", tags=["Cost of Living"])


@router.get(
    "/{city_id}/cost-of-living",
    response_model=ApiResponse[CityCostOfLivingResponse],
    summary="Get canonical cost-of-living basket metrics",
)
def get_city_cost_of_living(
    city_id: str,
    metric: str | None = Query(None, description="Optional specific cost metric name"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityCostOfLivingResponse]:
    """Retrieve canonical cost of living indicators. Returns explicit unavailable error if unrecorded."""
    service = CostOfLivingService(database)
    data = service.get_cost_of_living(city_id=city_id, metric=metric)

    metric_items = [CostOfLivingMetricItem(**item) for item in data.get("metrics", [])]

    return ApiResponse(
        data=CityCostOfLivingResponse(
            city_id=city_id,
            is_available=True,
            metric_count=data.get("metric_count", len(metric_items)),
            metrics=metric_items,
        ),
        meta=ResponseMeta(source="cost_of_living_canonical"),
    )
