"""Mobility & Transportation Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.city import CityService
from app.services.routing import RoutingService
from app.services.transit import TransitService


class MobilityAgent(BaseAgent):
    """Agent 3: Mobility / Transportation.

    Evaluates urban transit infrastructure, metropolitan connectivity,
    intra-city routing benchmarks, and GTFS public transit feed status.
    """

    def __init__(
        self,
        database: Database | None = None,
        city_service: CityService | None = None,
        transit_service: TransitService | None = None,
        routing_service: RoutingService | None = None,
    ) -> None:
        super().__init__(database)
        self.city_service = city_service or (CityService(database) if database is not None else None)
        self.transit_service = transit_service or (TransitService(database) if database is not None else None)
        self.routing_service = routing_service or (RoutingService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "mobility"

    @property
    def display_name(self) -> str:
        return "Mobility / Transportation"

    @property
    def scope(self) -> str:
        return "Urban transit infrastructure, metropolitan connectivity, and commute readiness"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.city_service:
            return self.create_unavailable_result("CityService not configured or database offline.", missing_data=("city_service",))

        try:
            city = self.city_service.get_city_details(request.city_id)
        except Exception:
            city = None

        if not city:
            return self.create_unavailable_result(f"City '{request.city_id}' not found.", missing_data=("city_record",))

        population = city.get("population") or 0
        capital_type = city.get("capital")
        is_metro = population >= 1_000_000
        is_major_hub = is_metro or capital_type in ("primary", "admin")

        sources: list[SourceProvenance] = [
            SourceProvenance(
                source_id="city_demographics",
                provider="canonical_city_registry",
                confidence=1.0,
            )
        ]
        warnings: list[str] = []
        unavailable_fields: list[str] = []

        # 1. Query Transit Service
        transit_info = None
        live_gtfs_connected = False
        if self.transit_service:
            try:
                transit_res = await self.transit_service.get_transit_info(city["city_id"])
                transit_meta = transit_res.get("meta", {})
                if transit_meta.get("status") == "fresh" and transit_res.get("transit"):
                    live_gtfs_connected = True
                    transit_info = transit_res["transit"]
                    sources.append(
                        SourceProvenance(
                            source_id="gtfs_transit",
                            provider=transit_meta.get("provider", "gtfs"),
                            confidence=0.9,
                        )
                    )
                else:
                    unavailable_fields.extend(["live_transit_feed", "gtfs_realtime"])
                    warnings.append(transit_meta.get("error_detail") or "Live GTFS transit feed not configured for this region.")
            except Exception as exc:
                warnings.append(f"Transit query error: {str(exc)}")
                unavailable_fields.append("transit")
        else:
            unavailable_fields.append("live_transit_feed")

        # 2. Query Routing Service for baseline urban commute sample
        route_data = None
        lat = city.get("latitude")
        lon = city.get("longitude")
        if self.routing_service and lat is not None and lon is not None:
            try:
                # Sample 5km corridor route from city center
                sample_route = await self.routing_service.calculate_route(
                    origin_lat=float(lat),
                    origin_lon=float(lon),
                    dest_lat=float(lat) + 0.04,
                    dest_lon=float(lon) + 0.04,
                    profile="driving",
                )
                if sample_route.get("route"):
                    route_data = sample_route["route"]
                    sources.append(
                        SourceProvenance(
                            source_id="urban_routing_osrm",
                            provider=sample_route.get("meta", {}).get("provider", "OSRM"),
                            confidence=0.9,
                        )
                    )
                else:
                    warnings.append("Sample urban route calculation unavailable from routing provider.")
            except Exception as exc:
                warnings.append(f"Routing check error: {str(exc)}")

        scale = "megacity" if population >= 5_000_000 else ("metropolis" if is_metro else "regional_urban")
        tier = "Tier-1 Multi-Modal" if is_major_hub else "Tier-2 Regional Transit"

        summary = (
            f"Metropolitan scale: {scale.capitalize()} (population {population:,}). "
            f"Transit tier: {tier} (Live GTFS: {'Connected' if live_gtfs_connected else 'Unconfigured'})."
        )
        if route_data:
            summary += f" Sample corridor route: {route_data.get('distance_km')} km in {route_data.get('duration_min')} min."

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE if live_gtfs_connected else AgentStatus.PARTIAL,
            data={
                "city_id": city["city_id"],
                "metropolitan_scale": scale,
                "capital_status": capital_type or "standard",
                "transit_infrastructure_tier": tier,
                "live_gtfs_connected": live_gtfs_connected,
                "transit_info": transit_info,
                "sample_commute_corridor": route_data,
                "note": "Mobility profile evaluated via demographic scale, GTFS availability, and OSRM routing.",
            },
            sources=tuple(sources),
            missing_data=tuple(unavailable_fields),
            unavailable_fields=tuple(unavailable_fields),
            warnings=tuple(warnings),
            detail="Metropolitan mobility profile evaluated from validated urban demographics and service routing.",
            summary=summary,
            confidence=0.85 if live_gtfs_connected else 0.75,
        )
