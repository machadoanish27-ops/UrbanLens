"""Environment & Climate Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.providers.base import LiveStatus
from app.services.air_quality import AirQualityService
from app.services.weather import WeatherService


class EnvironmentAgent(BaseAgent):
    """Agent 2: Environment / Climate.

    Synthesizes live meteorological feeds, WMO weather forecasts,
    and source-grounded air quality metrics from Open-Meteo, OpenAQ, and canonical baselines.
    """

    def __init__(
        self,
        database: Database | None = None,
        weather_service: WeatherService | None = None,
        air_quality_service: AirQualityService | None = None,
        knowledge_service: Any = None,
    ) -> None:
        super().__init__(database, knowledge_service=knowledge_service)
        self.weather_service = weather_service or (WeatherService(database) if database is not None else None)
        self.air_quality_service = air_quality_service or (AirQualityService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "environment"

    @property
    def display_name(self) -> str:
        return "Environment / Climate"

    @property
    def scope(self) -> str:
        return "Weather observations, WMO forecasts, and source-grounded air quality metrics"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.weather_service and not self.air_quality_service:
            return self.create_unavailable_result("Weather and AirQuality services not configured.", missing_data=("services",))

        sources: list[SourceProvenance] = []
        warnings: list[str] = []
        unavailable_fields: list[str] = []

        # 1. Fetch canonical baseline observations first for fallback/grounding
        canonical_weather = None
        forecasts = []
        if self.weather_service:
            try:
                w_db = self.weather_service.get_weather(request.city_id)
                canonical_weather = w_db.get("latest")
                fc_data = self.weather_service.get_forecast(request.city_id, limit=7)
                forecasts = fc_data.get("forecasts", [])
            except Exception:
                pass

        canonical_gw = None
        canonical_who = None
        if self.air_quality_service:
            try:
                aq_db = self.air_quality_service.get_air_quality(request.city_id)
                gw_list = aq_db.get("global_weather", [])
                who_list = aq_db.get("who_annual", [])
                if gw_list:
                    canonical_gw = gw_list[0]
                if who_list:
                    canonical_who = who_list[0]
            except Exception:
                pass

        # 2. Query live weather
        weather_res: dict[str, Any] | None = None
        weather_meta: dict[str, Any] = {}
        has_weather = False
        if self.weather_service:
            try:
                weather_res = await self.weather_service.get_live_weather(request.city_id)
                weather_meta = weather_res.get("meta", {})
                w_status = weather_meta.get("status")
                if w_status == LiveStatus.UNAVAILABLE or weather_res.get("weather") is None:
                    if canonical_weather:
                        has_weather = True
                        sources.append(
                            SourceProvenance(
                                source_id="weather_observations",
                                provider="mongodb",
                                observed_at=str(canonical_weather.get("observed_at")) if canonical_weather.get("observed_at") else None,
                                confidence=0.8,
                            )
                        )
                    else:
                        unavailable_fields.append("live_weather")
                        warnings.append(f"Weather unavailable: {weather_meta.get('error_detail') or 'No data'}")
                else:
                    has_weather = True
                    sources.append(
                        SourceProvenance(
                            source_id="weather",
                            provider=weather_meta.get("provider", "weather"),
                            observed_at=str(weather_meta.get("observed_at")) if weather_meta.get("observed_at") else None,
                            source_version="live_or_fallback_v1",
                            confidence=0.95 if w_status == LiveStatus.FRESH else 0.8,
                        )
                    )
            except Exception as exc:
                if canonical_weather:
                    has_weather = True
                    sources.append(
                        SourceProvenance(
                            source_id="weather_observations",
                            provider="mongodb",
                            observed_at=str(canonical_weather.get("observed_at")) if canonical_weather.get("observed_at") else None,
                            confidence=0.8,
                        )
                    )
                else:
                    warnings.append(f"Weather lookup failed: {str(exc)}")
                    unavailable_fields.append("weather")

        # 3. Query live air quality
        aq_res: dict[str, Any] | None = None
        aq_meta: dict[str, Any] = {}
        has_aq = False
        if self.air_quality_service:
            try:
                aq_res = await self.air_quality_service.get_live_air_quality(request.city_id)
                aq_meta = aq_res.get("meta", {})
                a_status = aq_meta.get("status")
                if a_status == LiveStatus.UNAVAILABLE or aq_res.get("air_quality") is None:
                    if canonical_gw or canonical_who:
                        has_aq = True
                    else:
                        unavailable_fields.append("live_air_quality")
                        warnings.append(f"Air quality unavailable: {aq_meta.get('error_detail') or 'No data'}")
                else:
                    has_aq = True
                    sources.append(
                        SourceProvenance(
                            source_id="air_quality",
                            provider=aq_meta.get("provider", "air_quality"),
                            observed_at=str(aq_meta.get("observed_at")) if aq_meta.get("observed_at") else None,
                            source_version="live_or_fallback_v1",
                            confidence=0.9 if a_status == LiveStatus.FRESH else 0.75,
                        )
                    )
            except Exception as exc:
                if canonical_gw or canonical_who:
                    has_aq = True
                else:
                    warnings.append(f"Air quality lookup failed: {str(exc)}")
                    unavailable_fields.append("air_quality")

        if canonical_gw:
            sources.append(
                SourceProvenance(
                    source_id="air_quality_global_weather",
                    provider=canonical_gw.get("provider", "global_weather"),
                    observed_at=str(canonical_gw.get("observed_at")) if canonical_gw.get("observed_at") else None,
                    confidence=0.85,
                )
            )
        if canonical_who:
            sources.append(
                SourceProvenance(
                    source_id="air_quality_who",
                    provider="WHO",
                    source_version=str(canonical_who.get("year", "2022")),
                    confidence=0.9,
                )
            )
        if forecasts:
            sources.append(
                SourceProvenance(
                    source_id="weather_forecasts_wmo",
                    provider="WMO",
                    observed_at=str(forecasts[0].get("fetched_at")) if forecasts[0].get("fetched_at") else None,
                    confidence=0.85,
                )
            )

        if not has_weather and not has_aq:
            return self.create_unavailable_result(
                f"No environmental or weather records found for city '{request.city_id}'.",
                missing_data=tuple(unavailable_fields) or ("weather", "air_quality"),
                warnings=tuple(warnings),
            )

        # Status determination
        if has_weather and has_aq:
            status = AgentStatus.COMPLETE
        elif has_weather or has_aq:
            status = AgentStatus.PARTIAL
        else:
            status = AgentStatus.UNAVAILABLE

        # Extract current weather values safely
        w_data = (weather_res or {}).get("weather") or {}
        w_curr = w_data.get("current") or canonical_weather or {}
        temp_c = w_curr.get("temperature_c")
        cond = w_curr.get("condition") or "clear"
        w_prov = weather_meta.get("provider") or (canonical_weather.get("provider") if canonical_weather else "mongodb")

        # Extract air quality values safely
        a_data = (aq_res or {}).get("air_quality") or {}
        pollutants = a_data.get("pollutants") or {}
        pm25 = pollutants.get("pm25") or (canonical_gw.get("pm25") if canonical_gw else None)
        aq_prov = aq_meta.get("provider") or (canonical_gw.get("provider") if canonical_gw else "mongodb")

        temp_str = f"{temp_c}°C ({cond})" if temp_c is not None else "N/A"
        pm_str = f"{pm25:.1f} µg/m³" if pm25 is not None else "N/A"
        summary = (
            f"Weather: {temp_str} via {w_prov}. Air Quality: PM2.5 {pm_str} via {aq_prov}."
        )

        # Retrieve grounded knowledge evidence
        ke_list = await self.retrieve_knowledge_evidence(
            query=request.query,
            city_id=request.city_id,
            categories=["environment"],
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
            status=status,
            data={
                "city_id": request.city_id,
                "current_weather": w_curr if w_curr else None,
                "weather_meta": weather_meta,
                "forecast_days_available": len(forecasts),
                "forecasts": forecasts[:3],
                "air_quality": a_data if a_data else None,
                "air_quality_meta": aq_meta,
                "air_quality_global_weather": canonical_gw or (a_data.get("global_weather") if isinstance(a_data, dict) else None),
                "air_quality_who_annual": canonical_who or (a_data.get("who_annual") if isinstance(a_data, dict) else None),
            },
            sources=tuple(sources),
            knowledge_evidence=tuple(ke_list),
            missing_data=tuple(unavailable_fields),
            unavailable_fields=tuple(unavailable_fields),
            warnings=tuple(warnings),
            detail="Environmental datasets retrieved through service layer with source provenance.",
            summary=summary,
            confidence=0.9 if status == AgentStatus.COMPLETE else 0.7,
            observed_at=weather_meta.get("observed_at") or aq_meta.get("observed_at"),
        )
