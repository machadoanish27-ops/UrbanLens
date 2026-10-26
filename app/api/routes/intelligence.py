"""Intelligence, domain agents, and orchestrator endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.intelligence import (
    AgentCatalogItem,
    AgentResultSchema,
    IntelligenceQueryRequest,
    IntelligenceQueryResponse,
    SourceProvenanceSchema,
)
from app.services.intelligence import IntelligenceService

router = APIRouter(tags=["Intelligence & Agents"])


@router.get(
    "/intelligence/agents",
    response_model=ApiResponse[list[AgentCatalogItem]],
    summary="List domain intelligence agents catalog",
)
def list_agents(
    database: Database = Depends(get_db),
) -> ApiResponse[list[AgentCatalogItem]]:
    """Return the seven UrbanLens domain agents, scopes, and active statuses."""
    service = IntelligenceService(database)
    catalog = service.list_agents()
    return ApiResponse(
        data=[AgentCatalogItem(**item) for item in catalog],
        meta=ResponseMeta(source="agent_catalog"),
    )


@router.post(
    "/intelligence/query",
    response_model=ApiResponse[IntelligenceQueryResponse],
    summary="Execute multi-agent intelligence query",
)
async def query_intelligence(
    request: IntelligenceQueryRequest,
    database: Database = Depends(get_db),
) -> ApiResponse[IntelligenceQueryResponse]:
    """Execute domain agents coordinated by the deterministic orchestrator for a city or query."""
    service = IntelligenceService(database)
    raw = await service.query_async(
        city_id=request.city_id,
        query=request.query,
        target_agents=request.agents,
    )

    results_objs = []
    for r in raw.get("results", []):
        sources = [SourceProvenanceSchema(**s) for s in r.get("sources", [])]
        results_objs.append(
            AgentResultSchema(
                agent_id=r["agent_id"],
                status=r["status"],
                data=r.get("data", {}),
                sources=sources,
                missing_data=r.get("missing_data", []),
                unavailable_fields=r.get("unavailable_fields", []),
                warnings=r.get("warnings", []),
                detail=r.get("detail"),
                summary=r.get("summary"),
                confidence=r.get("confidence", 1.0),
                observed_at=r.get("observed_at"),
                fetched_at=r.get("fetched_at"),
            )
        )

    all_sources_objs = [SourceProvenanceSchema(**s) for s in raw.get("sources", [])]

    return ApiResponse(
        data=IntelligenceQueryResponse(
            city_id=raw["city_id"],
            query=raw.get("query"),
            overall_status=raw["overall_status"],
            location=raw.get("location", {}),
            selected_agents=raw.get("selected_agents", []),
            results=results_objs,
            signals=raw.get("signals", []),
            summary=raw.get("summary"),
            warnings=raw.get("warnings", []),
            sources=all_sources_objs,
        ),
        meta=ResponseMeta(source="urbanlens_orchestrator"),
    )


@router.get(
    "/cities/{city_id}/intelligence",
    response_model=ApiResponse[IntelligenceQueryResponse],
    summary="Get multi-agent intelligence for a city",
)
async def get_city_intelligence(
    city_id: str,
    q: str | None = Query(None, description="Optional natural query context"),
    database: Database = Depends(get_db),
) -> ApiResponse[IntelligenceQueryResponse]:
    """Run all domain agents for a city and return aggregated intelligence."""
    service = IntelligenceService(database)
    raw = await service.query_async(city_id=city_id, query=q)

    results_objs = []
    for r in raw.get("results", []):
        sources = [SourceProvenanceSchema(**s) for s in r.get("sources", [])]
        results_objs.append(
            AgentResultSchema(
                agent_id=r["agent_id"],
                status=r["status"],
                data=r.get("data", {}),
                sources=sources,
                missing_data=r.get("missing_data", []),
                unavailable_fields=r.get("unavailable_fields", []),
                warnings=r.get("warnings", []),
                detail=r.get("detail"),
                summary=r.get("summary"),
                confidence=r.get("confidence", 1.0),
                observed_at=r.get("observed_at"),
                fetched_at=r.get("fetched_at"),
            )
        )

    all_sources_objs = [SourceProvenanceSchema(**s) for s in raw.get("sources", [])]

    return ApiResponse(
        data=IntelligenceQueryResponse(
            city_id=raw["city_id"],
            query=raw.get("query"),
            overall_status=raw["overall_status"],
            location=raw.get("location", {}),
            selected_agents=raw.get("selected_agents", []),
            results=results_objs,
            signals=raw.get("signals", []),
            summary=raw.get("summary"),
            warnings=raw.get("warnings", []),
            sources=all_sources_objs,
        ),
        meta=ResponseMeta(source="urbanlens_orchestrator"),
    )
