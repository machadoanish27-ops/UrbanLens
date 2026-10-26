"""Safety, Healthcare & Essential Information Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.air_quality import AirQualityService
from app.services.city import CityService
from app.services.country import CountryService
from app.services.places import PlacesService


class SafetyHealthcareAgent(BaseAgent):
    """Agent 7: Safety / Healthcare / Essential Information.

    Synthesizes environmental health criteria relative to WHO baselines,
    national public health indicators, and verified local healthcare facilities via PlacesService,
    while explicitly refusing to fabricate unavailable crime scores.
    """

    def __init__(
        self,
        database: Database | None = None,
        city_service: CityService | None = None,
        country_service: CountryService | None = None,
        air_quality_service: AirQualityService | None = None,
        places_service: PlacesService | None = None,
    ) -> None:
        super().__init__(database)
        self.city_service = city_service or (CityService(database) if database is not None else None)
        self.country_service = country_service or (CountryService(database) if database is not None else None)
        self.air_quality_service = air_quality_service or (AirQualityService(database) if database is not None else None)
        self.places_service = places_service or (PlacesService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "safety_healthcare"

    @property
    def display_name(self) -> str:
        return "Safety / Healthcare / Essentials"

    @property
    def scope(self) -> str:
        return "Environmental safety guidelines, public health indicators, and civic essentials"

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

        sources: list[SourceProvenance] = []
        warnings: list[str] = [
            "Neighborhood crime rates and emergency response times are unconfigured; safety scores are strictly non-fabricated."
        ]
        unavailable_fields: list[str] = [
            "neighborhood_crime_statistics",
            "emergency_dispatch_response_times",
            "violent_crime_index",
        ]

        # 1. Environmental health assessment via AirQualityService
        env_safety = {}
        if self.air_quality_service:
            try:
                aq_data = self.air_quality_service.get_air_quality(request.city_id)
                who_records = aq_data.get("who_annual", [])
                if who_records:
                    latest_who = who_records[0]
                    pm25 = latest_who.get("pm25_annual_mean_ug_m3")
                    if pm25 is not None:
                        env_safety["who_pm25_annual_ug_m3"] = pm25
                        env_safety["who_pm25_guideline_threshold_5ug"] = (
                            "Exceeds WHO annual guideline" if pm25 > 5.0 else "Within WHO guideline"
                        )
                        sources.append(
                            SourceProvenance(
                                source_id="air_quality_who_safety",
                                provider="WHO",
                                source_version=str(latest_who.get("year", "latest")),
                                confidence=0.9,
                            )
                        )
            except Exception:
                pass

        # 2. National health indicators via CountryService
        health_metrics = []
        country_id = city.get("country_id")
        if self.country_service and country_id:
            try:
                all_metrics = self.country_service.get_country_metrics(country_id)
                metrics_list = all_metrics.get("metrics", []) if isinstance(all_metrics, dict) else all_metrics
                health_metrics = [
                    m for m in metrics_list
                    if isinstance(m, dict) and any(k in m.get("metric", "").lower() for k in ("health", "life", "mortality", "hospital", "sanitation"))
                ]
                if health_metrics:
                    sources.append(
                        SourceProvenance(
                            source_id="country_health_metrics",
                            provider="national_macro_registry",
                            confidence=0.9,
                        )
                    )
            except Exception:
                pass

        # 3. Live healthcare facilities search via PlacesService
        healthcare_places = []
        lat = city.get("latitude")
        lon = city.get("longitude")
        if self.places_service and lat is not None and lon is not None:
            try:
                places_res = await self.places_service.search_places(
                    latitude=float(lat),
                    longitude=float(lon),
                    category="hospital",
                    radius=3000,
                    limit=5,
                )
                healthcare_places = places_res.get("places", [])
                if healthcare_places:
                    sources.append(
                        SourceProvenance(
                            source_id="healthcare_facilities_overpass",
                            provider="openstreetmap_overpass",
                            confidence=0.9,
                        )
                    )
            except Exception:
                pass

        has_data = bool(env_safety or health_metrics or healthcare_places)
        if not has_data:
            return self.create_unavailable_result(
                f"No verified safety or healthcare metrics recorded for city '{request.city_id}'.",
                missing_data=("safety_metrics", "healthcare_metrics"),
                unavailable_fields=tuple(unavailable_fields),
                warnings=tuple(warnings),
            )

        status = AgentStatus.COMPLETE if (env_safety and (healthcare_places or health_metrics)) else AgentStatus.PARTIAL

        hosp_summary = f"{len(healthcare_places)} hospital/medical facilities identified" if healthcare_places else "Medical POI data pending"
        env_summary = f"WHO PM2.5: {env_safety.get('who_pm25_annual_ug_m3')} µg/m³ ({env_safety.get('who_pm25_guideline_threshold_5ug')})" if env_safety else "Environmental health pending"
        summary = f"Healthcare infrastructure: {hosp_summary}. Environmental health: {env_summary}. Crime data: unconfigured."

        return AgentResult(
            agent_id=self.agent_id,
            status=status,
            data={
                "city_id": city["city_id"],
                "environmental_health": env_safety,
                "national_health_indicators": [
                    {"metric": m.get("metric"), "period": m.get("period"), "value": m.get("value"), "unit": m.get("unit")}
                    for m in health_metrics[:5]
                ],
                "healthcare_facilities_count": len(healthcare_places),
                "healthcare_facilities": healthcare_places,
                "explicitly_unavailable": {
                    "neighborhood_crime_statistics": "Data source not configured",
                    "emergency_response_times": "Data source not configured",
                },
            },
            sources=tuple(sources),
            missing_data=() if status == AgentStatus.COMPLETE else ("complete_safety_profile",),
            unavailable_fields=tuple(unavailable_fields),
            warnings=tuple(warnings),
            detail="Safety and health profile compiled from environmental observations, national metrics, and verified medical POIs.",
            summary=summary,
            confidence=0.85 if status == AgentStatus.COMPLETE else 0.7,
        )
