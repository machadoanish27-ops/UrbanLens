"""Accommodation & Locality Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.core.exceptions import DataUnavailableException
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.city import CityService
from app.services.cost import CostOfLivingService
from app.services.places import PlacesService


class AccommodationAgent(BaseAgent):
    """Agent 5: Accommodation / Locality.

    Examines residential rental benchmarks, neighborhood amenities,
    and locality pricing dynamics while explicitly distinguishing unavailable fields.
    """

    def __init__(
        self,
        database: Database | None = None,
        cost_service: CostOfLivingService | None = None,
        city_service: CityService | None = None,
        places_service: PlacesService | None = None,
    ) -> None:
        super().__init__(database)
        self.cost_service = cost_service or (CostOfLivingService(database) if database is not None else None)
        self.city_service = city_service or (CityService(database) if database is not None else None)
        self.places_service = places_service or (PlacesService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "accommodation"

    @property
    def display_name(self) -> str:
        return "Accommodation / Locality"

    @property
    def scope(self) -> str:
        return "Residential rental benchmarks, neighborhood density, and housing indices"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.cost_service:
            return self.create_unavailable_result("CostOfLivingService not configured.", missing_data=("cost_service",))

        try:
            col_data = self.cost_service.get_cost_of_living(request.city_id)
            metrics = col_data.get("metrics", [])
        except DataUnavailableException:
            metrics = []
        except Exception:
            metrics = []

        rental_metrics = {}
        for m in metrics:
            metric_name = m.get("metric", "").lower()
            if any(term in metric_name for term in ("rent", "apartment", "price per square")):
                rental_metrics[m["metric"]] = {
                    "value": m.get("value"),
                    "unit": m.get("unit"),
                }

        if not rental_metrics:
            return self.create_unavailable_result(
                f"No verified residential rental metrics available for city '{request.city_id}'.",
                missing_data=("rental_housing_metrics",),
                unavailable_fields=(
                    "rental_housing_metrics",
                    "neighborhood_vacancy_rates",
                    "short_term_rental_yield",
                    "verified_real_estate_listings",
                ),
            )

        sources: list[SourceProvenance] = [
            SourceProvenance(
                source_id="cost_of_living_rental",
                provider="canonical_cost_dataset",
                confidence=0.9,
            )
        ]
        warnings: list[str] = [
            "Individual rental unit listings and micro-neighborhood vacancy rates are unconfigured; baseline aggregates shown."
        ]
        unavailable_fields: list[str] = [
            "neighborhood_vacancy_rates",
            "short_term_rental_yield",
            "verified_real_estate_listings",
            "individual_landlord_ratings",
        ]

        # Query PlacesService for neighborhood / residential amenities if coordinates exist
        amenities = []
        if self.city_service and self.places_service:
            try:
                city = self.city_service.get_city_details(request.city_id)
                lat = city.get("latitude")
                lon = city.get("longitude")
                if lat is not None and lon is not None:
                    places_res = await self.places_service.search_places(
                        latitude=float(lat),
                        longitude=float(lon),
                        category="supermarket",
                        radius=2500,
                        limit=5,
                    )
                    amenities = places_res.get("places", [])
                    if amenities:
                        sources.append(
                            SourceProvenance(
                                source_id="neighborhood_amenities",
                                provider="openstreetmap_overpass",
                                confidence=0.85,
                            )
                        )
            except Exception:
                pass

        summary = (
            f"Residential baseline: {len(rental_metrics)} rental indices cataloged. "
            f"Locality amenities sampled: {len(amenities)} convenience/residential hubs verified."
        )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": request.city_id,
                "housing_metrics_count": len(rental_metrics),
                "housing_metrics": rental_metrics,
                "locality_amenities_count": len(amenities),
                "locality_amenities": amenities,
                "explicitly_unavailable": {
                    "vacancy_rates": "Data source not configured",
                    "live_listing_inventory": "Data source not configured",
                },
            },
            sources=tuple(sources),
            missing_data=(),
            unavailable_fields=tuple(unavailable_fields),
            warnings=tuple(warnings),
            detail="Housing and accommodation benchmarks grounded in validated basket entries and locality POIs.",
            summary=summary,
            confidence=0.85,
        )
