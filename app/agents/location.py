"""Location & City Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.city import CityRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class LocationAgent(BaseAgent):
    """Agent 1: Location / City Intelligence.
    
    Responsible for city identity, geospatial coordinates, administrative hierarchy,
    canonical IDs, recognized aliases, and provider-specific mappings.
    """

    @property
    def agent_id(self) -> str:
        return "location"

    @property
    def display_name(self) -> str:
        return "Location / City Intelligence"

    @property
    def scope(self) -> str:
        return "City identity, coordinates, administrative boundary, and provider resolution"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        repo = CityRepository(self.database)
        city = repo.get_by_city_id(request.city_id)
        if not city:
            # Try resolving alias
            resolved_id = repo.resolve_alias_to_city_id(request.city_id)
            if resolved_id:
                city = repo.get_by_city_id(resolved_id)

        if not city:
            return self.create_unavailable_result(
                f"City '{request.city_id}' could not be located in canonical database.",
                missing_data=("city_record",),
            )

        canonical_id = city["city_id"]
        aliases = repo.get_aliases(canonical_id)
        identities = repo.get_provider_identities(canonical_id)

        sources = (
            SourceProvenance(
                source_id=city.get("source_id", "worldcities"),
                provider="canonical_city_registry",
                source_version=city.get("mapping_version", "1.0"),
            ),
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
                "aliases": [a.get("alias") for a in aliases[:10]],
                "provider_identities": [
                    {"provider": i.get("provider"), "provider_location_id": i.get("provider_location_id")}
                    for i in identities
                ],
            },
            sources=sources,
            missing_data=(),
            detail="Canonical location and administrative identity successfully verified.",
        )
