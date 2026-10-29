"""Education, Culture & Lifestyle Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.city import CityService
from app.services.places import PlacesService
from app.services.university import UniversityService


class EducationLifestyleAgent(BaseAgent):
    """Agent 6: Education / Culture / Lifestyle.

    Profiles academic ecosystems, presence of accredited universities,
    global institution rankings, and local cultural points of interest.
    """

    def __init__(
        self,
        database: Database | None = None,
        city_service: CityService | None = None,
        university_service: UniversityService | None = None,
        places_service: PlacesService | None = None,
        knowledge_service: Any = None,
    ) -> None:
        super().__init__(database, knowledge_service=knowledge_service)
        self.city_service = city_service or (CityService(database) if database is not None else None)
        self.university_service = university_service or (UniversityService(database) if database is not None else None)
        self.places_service = places_service or (PlacesService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "education_culture"

    @property
    def display_name(self) -> str:
        return "Education / Culture / Lifestyle"

    @property
    def scope(self) -> str:
        return "Higher education institutions, global university rankings, and academic culture"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.city_service or not self.university_service:
            return self.create_unavailable_result("City and University services not configured.", missing_data=("services",))

        try:
            city = self.city_service.get_city_details(request.city_id)
        except Exception:
            city = None

        if not city:
            return self.create_unavailable_result(f"City '{request.city_id}' not found.", missing_data=("city_record",))

        country_iso2 = city.get("country_iso2")
        country_id = city.get("country_id")

        try:
            univ_items, total_univs = self.university_service.get_universities_by_city(
                request.city_id,
                page=1,
                page_size=10,
            )
        except Exception:
            univ_items, total_univs = ([], 0)

        languages = city.get("languages") or {}

        sources: list[SourceProvenance] = []
        warnings: list[str] = []

        if total_univs == 0:
            return self.create_unavailable_result(
                f"No registered universities found in academic directory for country '{country_iso2 or country_id}'.",
                missing_data=("universities",),
            )

        sources.append(
            SourceProvenance(
                source_id="universities",
                provider="canonical_university_registry",
                confidence=1.0,
            )
        )

        if languages.get("status") == "available":
            sources.append(
                SourceProvenance(
                    source_id="un_iso_languages",
                    provider=languages.get("source") or "ISO-639 / UN Linguistic Statistics",
                    confidence=1.0,
                )
            )

        sample_institutions = []
        for u in univ_items:
            uid = u.get("university_id")
            rankings = []
            if uid:
                try:
                    rankings = self.university_service.get_university_rankings(uid)
                except Exception:
                    pass
            sample_institutions.append({
                "university_id": uid,
                "name": u.get("name"),
                "website": u.get("website"),
                "data_source": "canonical_database",
                "latest_rankings": [
                    {"metric": r.get("ranking_metric"), "year": r.get("ranking_year"), "value": r.get("value")}
                    for r in rankings[:2]
                ],
            })

        # Query PlacesService for educational/cultural POIs (libraries, museums, etc.)
        cultural_places = []
        lat = city.get("latitude")
        lon = city.get("longitude")
        if self.places_service and lat is not None and lon is not None:
            try:
                places_res = await self.places_service.search_places(
                    latitude=float(lat),
                    longitude=float(lon),
                    category="library",
                    radius=3000,
                    limit=5,
                )
                cultural_places = places_res.get("places", [])
                if cultural_places:
                    sources.append(
                        SourceProvenance(
                            source_id="cultural_amenities",
                            provider="openstreetmap_overpass",
                            confidence=0.85,
                        )
                    )
            except Exception:
                pass

        lang_part = ""
        if languages and languages.get("status") == "available":
            officials = ", ".join(languages.get("official_languages", []))
            lang_part = f" Official/Spoken languages: {officials} (country-level)."

        summary = (
            f"Academic ecosystem: {total_univs} higher education institutions cataloged. "
            f"Top sample: {sample_institutions[0]['name'] if sample_institutions else 'None'}. "
            f"Cultural POIs located: {len(cultural_places)} libraries/cultural venues.{lang_part}"
        )

        # Retrieve grounded knowledge evidence
        ke_list = await self.retrieve_knowledge_evidence(
            query=request.query,
            city_id=city["city_id"],
            categories=["education", "culture", "lifestyle"],
            top_k=2,
        )
        for ev in ke_list:
            sources.append(
                SourceProvenance(
                    source_id=ev.source,
                    provider="knowledge",
                    retrieved_at=ev.retrieved_at,
                    confidence=ev.retrieval_score or 1.0,
                )
            )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": city["city_id"],
                "country_iso2": country_iso2,
                "total_country_institutions": total_univs,
                "sample_institutions": sample_institutions,
                "languages": languages,
                "cultural_poi_count": len(cultural_places),
                "cultural_pois": cultural_places,
                "database_derived_fields": ["total_country_institutions", "sample_institutions", "rankings", "languages"],
                "live_derived_fields": ["cultural_pois"],
            },
            sources=tuple(sources),
            knowledge_evidence=tuple(ke_list),
            missing_data=(),
            unavailable_fields=(),
            warnings=tuple(warnings),
            detail="Regional higher education institutions and cultural infrastructure cataloged.",
            summary=summary,
            confidence=0.9,
        )
