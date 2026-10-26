"""Location & City Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.core.exceptions import ResourceNotFoundException
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.city import CityService
from app.services.geocoding import GeocodingService
from app.services.places import PlacesService


class LocationAgent(BaseAgent):
    """Agent 1: Location / City Intelligence.

    Responsible for canonical city identity, geospatial coordinates, administrative hierarchy,
    canonical IDs, recognized aliases, and provider-specific mappings.
    """

    def __init__(
        self,
        database: Database | None = None,
        city_service: CityService | None = None,
        geocoding_service: GeocodingService | None = None,
        places_service: PlacesService | None = None,
        knowledge_service: Any = None,
    ) -> None:
        super().__init__(database, knowledge_service=knowledge_service)
        self.city_service = city_service or (CityService(database) if database is not None else None)
        self.geocoding_service = geocoding_service or (GeocodingService(database) if database is not None else None)
        self.places_service = places_service or (PlacesService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "location"

    @property
    def display_name(self) -> str:
        return "Location / City Intelligence"

    @property
    def scope(self) -> str:
        return "City identity, coordinates, administrative boundary, and provider resolution"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.city_service:
            return self.create_unavailable_result("CityService not configured or database offline.", missing_data=("city_service",))

        try:
            city = self.city_service.get_city_details(request.city_id)
        except ResourceNotFoundException:
            return self.create_unavailable_result(
                f"City '{request.city_id}' could not be located in canonical database.",
                missing_data=("city_record",),
            )
        except Exception as exc:
            return self.create_unavailable_result(
                f"Error retrieving canonical city details: {str(exc)}",
                missing_data=("city_record",),
            )

        if not city:
            return self.create_unavailable_result(
                f"City '{request.city_id}' could not be located in canonical database.",
                missing_data=("city_record",),
            )

        canonical_id = city["city_id"]
        aliases = city.get("aliases", [])
        identities = city.get("provider_identities", [])

        sources_list: list[SourceProvenance] = [
            SourceProvenance(
                source_id=city.get("source_id", "worldcities"),
                provider="canonical_city_registry",
                source_version=city.get("mapping_version", "1.0"),
                confidence=1.0,
            ),
        ]

        # Retrieve grounded knowledge evidence
        ke_list = await self.retrieve_knowledge_evidence(
            query=request.query,
            city_id=canonical_id,
            categories=["city_information", "relocation", "culture"],
            top_k=2,
        )
        for ev in ke_list:
            sources_list.append(
                SourceProvenance(
                    source_id=ev.source,
                    provider="knowledge",
                    retrieved_at=ev.retrieved_at,
                    confidence=ev.retrieval_score or 1.0,
                )
            )

        pop = city.get("population")
        pop_str = f"{pop:,}" if isinstance(pop, (int, float)) else "N/A"
        summary = (
            f"Location verified: {city.get('name')}, {city.get('country_iso2') or city.get('country_id') or 'N/A'}. "
            f"Administrative region: {city.get('admin_name') or 'N/A'}, population: {pop_str}."
        )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": canonical_id,
                "name": city.get("name"),
                "name_ascii": city.get("name_ascii"),
                "country_id": city.get("country_id"),
                "country_iso2": city.get("country_iso2"),
                "country_iso3": city.get("country_iso3"),
                "admin_name": city.get("admin_name"),
                "capital": city.get("capital"),
                "population": city.get("population"),
                "latitude": city.get("latitude"),
                "longitude": city.get("longitude"),
                "alias_count": len(aliases),
                "aliases": [a.get("alias") for a in aliases[:10] if isinstance(a, dict)],
                "provider_identities": [
                    {"provider": i.get("provider"), "provider_location_id": i.get("provider_location_id")}
                    for i in identities
                    if isinstance(i, dict)
                ],
            },
            sources=tuple(sources_list),
            knowledge_evidence=tuple(ke_list),
            missing_data=(),
            unavailable_fields=(),
            detail="Canonical location and administrative identity successfully verified.",
            summary=summary,
            confidence=1.0,
        )
