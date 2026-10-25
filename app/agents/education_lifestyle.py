"""Education, Culture & Lifestyle Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.city import CityRepository
from app.db.repositories.university import UniversityRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class EducationLifestyleAgent(BaseAgent):
    """Agent 6: Education / Culture / Lifestyle.
    
    Profiles academic ecosystems, presence of accredited universities,
    and global institution rankings.
    """

    @property
    def agent_id(self) -> str:
        return "education_culture"

    @property
    def display_name(self) -> str:
        return "Education / Culture / Lifestyle"

    @property
    def scope(self) -> str:
        return "Higher education institutions, global university rankings, and academic culture"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        city_repo = CityRepository(self.database)
        univ_repo = UniversityRepository(self.database)

        city = city_repo.get_by_city_id(request.city_id)
        if not city:
            return self.create_unavailable_result(f"City '{request.city_id}' not found.", missing_data=("city_record",))

        country_iso2 = city.get("country_iso2")
        country_id = city.get("country_id")

        univ_items, total_univs = ([], 0)
        if country_iso2 or country_id:
            univ_items, total_univs = univ_repo.get_universities_by_country(
                country_iso2=country_iso2,
                country_id=country_id,
                page=1,
                page_size=10,
            )

        if total_univs == 0:
            return self.create_unavailable_result(
                f"No registered universities found in academic directory for country '{country_iso2 or country_id}'.",
                missing_data=("universities",),
            )

        sources = (
            SourceProvenance(
                source_id="universities",
                provider="canonical_university_registry",
            ),
        )

        sample_institutions = []
        for u in univ_items:
            uid = u.get("university_id")
            rankings = univ_repo.get_rankings(uid) if uid else []
            sample_institutions.append({
                "university_id": uid,
                "name": u.get("name"),
                "website": u.get("website"),
                "latest_rankings": [
                    {"metric": r.get("ranking_metric"), "year": r.get("ranking_year"), "value": r.get("value")}
                    for r in rankings[:2]
                ],
            })

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": city["city_id"],
                "country_iso2": country_iso2,
                "total_country_institutions": total_univs,
                "sample_institutions": sample_institutions,
            },
            sources=sources,
            missing_data=(),
            detail="Regional higher education institutions cataloged with rankings.",
        )
