"""Cost of Living & Budget Intelligence Agent."""

from typing import Any
from pymongo.database import Database

from app.agents.base import BaseAgent
from app.core.exceptions import DataUnavailableException
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.services.city import CityService
from app.services.cost import CostOfLivingService
from app.services.currency import CurrencyService


class CostAgent(BaseAgent):
    """Agent 4: Cost of Living / Budget.

    Grounds municipal budget requirements, consumer price indices,
    and relative affordability metrics using verified basket benchmarks
    and live currency exchange rates.
    """

    def __init__(
        self,
        database: Database | None = None,
        cost_service: CostOfLivingService | None = None,
        currency_service: CurrencyService | None = None,
        city_service: CityService | None = None,
        knowledge_service: Any = None,
    ) -> None:
        super().__init__(database, knowledge_service=knowledge_service)
        self.cost_service = cost_service or (CostOfLivingService(database) if database is not None else None)
        self.currency_service = currency_service or (CurrencyService(database) if database is not None else None)
        self.city_service = city_service or (CityService(database) if database is not None else None)

    @property
    def agent_id(self) -> str:
        return "cost_of_living"

    @property
    def display_name(self) -> str:
        return "Cost-of-Living / Budget"

    @property
    def scope(self) -> str:
        return "Consumer basket metrics, rental indices, and city living expense benchmarks"

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.cost_service:
            return self.create_unavailable_result("CostOfLivingService not configured or database offline.", missing_data=("cost_service",))

        try:
            col_data = self.cost_service.get_cost_of_living(request.city_id)
            metrics = col_data.get("metrics", [])
        except DataUnavailableException:
            return self.create_unavailable_result(
                f"No verified cost-of-living metrics found for city '{request.city_id}'. Estimates are strictly non-fabricated.",
                missing_data=("cost_of_living_metrics",),
            )
        except Exception as exc:
            return self.create_unavailable_result(
                f"Error fetching cost-of-living metrics: {str(exc)}",
                missing_data=("cost_of_living_metrics",),
            )

        if not metrics:
            return self.create_unavailable_result(
                f"No verified cost-of-living metrics found for city '{request.city_id}'. Estimates are strictly non-fabricated.",
                missing_data=("cost_of_living_metrics",),
            )

        sources: list[SourceProvenance] = [
            SourceProvenance(
                source_id="cost_of_living",
                provider=metrics[0].get("source_id", "canonical_cost_dataset"),
                observed_at=str(metrics[0].get("observed_at")) if metrics[0].get("observed_at") else None,
                confidence=0.9,
            )
        ]
        warnings: list[str] = []
        unavailable_fields: list[str] = []

        # Determine target currency from country
        target_currency = "USD"
        if self.city_service:
            try:
                city = self.city_service.get_city_details(request.city_id)
                iso2 = (city.get("country_iso2") or "").upper()
                from app.data.currencies import get_currency_for_country
                curr_dict = get_currency_for_country(iso2)
                target_currency = curr_dict.get("code", "USD")
            except Exception:
                pass

        # Query CurrencyService for live FX rate between USD and target currency
        live_fx = None
        if self.currency_service and target_currency != "USD":
            try:
                fx_res = await self.currency_service.convert_currency("USD", target_currency, amount=1.0)
                fx_meta = fx_res.get("meta", {})
                fx_status = fx_res.get("status") or fx_meta.get("status")
                conv_dict = fx_res.get("conversion") if isinstance(fx_res.get("conversion"), dict) else {}
                rate = fx_res.get("rate") or conv_dict.get("rate")
                if fx_status in ("fresh", "cached", "live") and rate is not None:
                    live_fx = fx_res.get("conversion") or {
                        "from_currency": "USD",
                        "to_currency": target_currency,
                        "rate": rate,
                        "converted_amount": fx_res.get("converted_amount") or conv_dict.get("converted_amount") or rate,
                    }
                    sources.append(
                        SourceProvenance(
                            source_id="live_fx_rates",
                            provider=fx_res.get("provider") or fx_meta.get("provider", "frankfurter"),
                            observed_at=str(fx_res.get("observed_at") or fx_meta.get("observed_at")) if (fx_res.get("observed_at") or fx_meta.get("observed_at")) else None,
                            confidence=0.95 if fx_status == "fresh" else 0.90,
                        )
                    )
                else:
                    unavailable_fields.append("live_fx_rates")
                    warnings.append(fx_meta.get("error_detail") or "Live foreign exchange rate provider unavailable.")
            except Exception as exc:
                warnings.append(f"Currency conversion error: {str(exc)}")
                unavailable_fields.append("live_fx_rates")

        metrics_map = {m["metric"]: m.get("value") for m in metrics if "metric" in m}

        fx_summary = (
            f" Live FX: 1 USD = {live_fx.get('converted_amount')} {target_currency}."
            if live_fx
            else " (Live FX conversion unavailable)."
        )
        summary = (
            f"Canonical cost baseline grounded: {len(metrics)} basket metrics recorded.{fx_summary}"
        )

        # Retrieve grounded knowledge evidence
        ke_list = await self.retrieve_knowledge_evidence(
            query=request.query,
            city_id=request.city_id,
            categories=["housing", "relocation"],
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
                "city_id": request.city_id,
                "metrics_recorded_count": len(metrics),
                "metrics": metrics_map,
                "live_exchange_rate": live_fx,
                "data_source_mode": "canonical_baseline_with_live_fx" if live_fx else "canonical_baseline_only",
            },
            sources=tuple(sources),
            knowledge_evidence=tuple(ke_list),
            missing_data=tuple(unavailable_fields),
            unavailable_fields=tuple(unavailable_fields),
            warnings=tuple(warnings),
            detail="Canonical cost-of-living metrics retrieved without interpolation; live FX rate integrated where available.",
            summary=summary,
            confidence=0.95 if live_fx else 0.85,
        )
