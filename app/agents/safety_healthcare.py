"""Safety, Healthcare & Essential Information Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.air_quality import AirQualityRepository
from app.db.repositories.city import CityRepository
from app.db.repositories.country import CountryRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class SafetyHealthcareAgent(BaseAgent):
    """Agent 7: Safety / Healthcare / Essential Information.
    
    Synthesizes environmental health criteria (particulate matter relative to WHO safety baselines),
    national public health metrics, and essential civic infrastructure.
    """

    @property
    def agent_id(self) -> str:
        return "safety_healthcare"

    @property
    def display_name(self) -> str:
        return "Safety / Healthcare / Essentials"

    @property
    def scope(self) -> str:
        return "Environmental safety guidelines, public health indicators, and civic essentials"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        city_repo = CityRepository(self.database)
        aq_repo = AirQualityRepository(self.database)
        country_repo = CountryRepository(self.database)

        city = city_repo.get_by_city_id(request.city_id)
        if not city:
            return self.create_unavailable_result(f"City '{request.city_id}' not found.", missing_data=("city_record",))

        latest_aq_gw = aq_repo.get_latest_global_weather_aq(request.city_id)
        latest_aq_who = aq_repo.get_latest_who_aq(request.city_id)

        country_id = city.get("country_id")
        health_metrics = []
        if country_id:
            all_metrics = country_repo.get_metrics(country_id)
            health_metrics = [
                m for m in all_metrics
                if any(k in m.get("metric", "").lower() for k in ("health", "life", "mortality", "hospital", "sanitation"))
            ]

        sources: list[SourceProvenance] = []
        if latest_aq_gw or latest_aq_who:
            sources.append(
                SourceProvenance(
                    source_id="air_quality_safety",
                    provider="WHO/GlobalWeather",
                )
            )
        if health_metrics:
            sources.append(
                SourceProvenance(
                    source_id="country_metrics",
                    provider="national_macro_registry",
                )
            )

        # Environmental health threshold check (WHO guideline: annual PM2.5 <= 5 µg/m³)
        env_safety = {}
        if latest_aq_who:
            pm25 = latest_aq_who.get("pm25_annual_mean_ug_m3")
            if pm25 is not None:
                env_safety["who_pm25_annual_ug_m3"] = pm25
                env_safety["who_pm25_guideline_threshold_5ug"] = (
                    "Exceeds WHO annual guideline" if pm25 > 5.0 else "Within WHO guideline"
                )

        if not sources and not env_safety:
            return self.create_unavailable_result(
                f"No verified safety or healthcare metrics recorded for city '{request.city_id}'.",
                missing_data=("safety_metrics", "healthcare_metrics"),
            )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE if (env_safety and health_metrics) else AgentStatus.PARTIAL,
            data={
                "city_id": city["city_id"],
                "environmental_health": env_safety,
                "national_health_indicators": [
                    {"metric": m.get("metric"), "period": m.get("period"), "value": m.get("value"), "unit": m.get("unit")}
                    for m in health_metrics[:5]
                ],
            },
            sources=tuple(sources),
            missing_data=() if (env_safety and health_metrics) else ("complete_safety_profile",),
            detail="Safety and health profile compiled from environmental observations and national metrics.",
        )
