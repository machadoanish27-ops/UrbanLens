"""Environment & Climate Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.weather import WeatherRepository
from app.db.repositories.air_quality import AirQualityRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class EnvironmentAgent(BaseAgent):
    """Agent 2: Environment / Climate.
    
    Synthesizes meteorological observations, WMO weather forecasts,
    and air quality assessments from Global Weather and WHO monitoring sources.
    """

    @property
    def agent_id(self) -> str:
        return "environment"

    @property
    def display_name(self) -> str:
        return "Environment / Climate"

    @property
    def scope(self) -> str:
        return "Weather observations, WMO forecasts, and source-grounded air quality metrics"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        weather_repo = WeatherRepository(self.database)
        aq_repo = AirQualityRepository(self.database)

        latest_weather = weather_repo.get_latest_observation(request.city_id)
        forecasts = weather_repo.get_forecasts(request.city_id, limit=7)
        aq_gw = aq_repo.get_latest_global_weather_aq(request.city_id)
        aq_who = aq_repo.get_latest_who_aq(request.city_id)

        sources: list[SourceProvenance] = []
        if latest_weather:
            sources.append(
                SourceProvenance(
                    source_id="weather_observations",
                    provider=latest_weather.get("provider", "weather"),
                    observed_at=str(latest_weather.get("observed_at")) if latest_weather.get("observed_at") else None,
                )
            )
        if forecasts:
            sources.append(
                SourceProvenance(
                    source_id="weather_forecasts_wmo",
                    provider="WMO",
                    observed_at=str(forecasts[0].get("fetched_at")) if forecasts[0].get("fetched_at") else None,
                )
            )
        if aq_gw:
            sources.append(
                SourceProvenance(
                    source_id="air_quality_global_weather",
                    provider=aq_gw.get("provider", "global_weather"),
                    observed_at=str(aq_gw.get("observed_at")) if aq_gw.get("observed_at") else None,
                )
            )
        if aq_who:
            sources.append(
                SourceProvenance(
                    source_id="air_quality_who",
                    provider="WHO",
                    source_version=str(aq_who.get("year")),
                )
            )

        has_weather = latest_weather is not None or len(forecasts) > 0
        has_aq = aq_gw is not None or aq_who is not None

        if not has_weather and not has_aq:
            return self.create_unavailable_result(
                f"No environmental or weather records found for city '{request.city_id}'.",
                missing_data=("weather_observations", "air_quality"),
            )

        status = AgentStatus.COMPLETE if (has_weather and has_aq) else AgentStatus.PARTIAL
        missing = () if (has_weather and has_aq) else (("air_quality",) if not has_aq else ("weather",))

        return AgentResult(
            agent_id=self.agent_id,
            status=status,
            data={
                "current_weather": latest_weather,
                "forecast_days_available": len(forecasts),
                "forecasts": forecasts[:3],
                "air_quality_global_weather": aq_gw,
                "air_quality_who_annual": aq_who,
            },
            sources=tuple(sources),
            missing_data=missing,
            detail="Environmental datasets retrieved with full source provenance.",
        )
