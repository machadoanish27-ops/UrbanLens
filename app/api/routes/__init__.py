"""API routes configuration bundling all endpoint routers."""

from fastapi import APIRouter

from app.api.routes.air_quality import router as air_quality_router
from app.api.routes.cities import router as cities_router
from app.api.routes.cost import router as cost_router
from app.api.routes.countries import router as countries_router
from app.api.routes.currency import router as currency_router
from app.api.routes.geocoding import router as geocoding_router
from app.api.routes.health import router as health_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.places import router as places_router
from app.api.routes.routing import router as routing_router
from app.api.routes.transit import router as transit_router
from app.api.routes.universities import router as universities_router
from app.api.routes.weather import router as weather_router
from app.services.orchestrator import AgentOrchestrator

# Root router for top-level health checks and legacy compatibility
root_router = APIRouter()
root_router.include_router(health_router)


@root_router.get("/agents", tags=["Legacy Compatibility"], include_in_schema=False)
def legacy_list_agents() -> dict[str, list[dict[str, str | bool]]]:
    """Legacy backward-compatible agents endpoint."""
    return {"agents": AgentOrchestrator().catalog()}


# API v1 router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(cities_router)
api_v1_router.include_router(countries_router)
api_v1_router.include_router(weather_router)
api_v1_router.include_router(air_quality_router)
api_v1_router.include_router(cost_router)
api_v1_router.include_router(currency_router)
api_v1_router.include_router(geocoding_router)
api_v1_router.include_router(routing_router)
api_v1_router.include_router(places_router)
api_v1_router.include_router(transit_router)
api_v1_router.include_router(universities_router)
api_v1_router.include_router(intelligence_router)
api_v1_router.include_router(knowledge_router)

__all__ = ["root_router", "api_v1_router"]
