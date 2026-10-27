"""UrbanLens multi-agent orchestrator."""

import asyncio
import concurrent.futures
import re
from typing import Any, Sequence
from pymongo.database import Database

from app.agents.accommodation import AccommodationAgent
from app.agents.base import BaseAgent
from app.agents.catalog import AGENT_CATALOG
from app.agents.cost import CostAgent
from app.agents.education_lifestyle import EducationLifestyleAgent
from app.agents.environment import EnvironmentAgent
from app.agents.location import LocationAgent
from app.agents.mobility import MobilityAgent
from app.agents.safety_healthcare import SafetyHealthcareAgent
from app.db.repositories.city import CityRepository
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.models.knowledge import KnowledgeEvidence
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.result import AggregatedIntelligence
from app.schemas.llm import LLMAskResponse
from app.services.knowledge import KnowledgeService
from app.services.llm import LLMService


class UrbanLensOrchestrator:
    """Multi-agent orchestrator coordinating domain agents to generate grounded city intelligence."""

    def __init__(
        self,
        database: Database | None = None,
        agents: dict[str, BaseAgent] | None = None,
        knowledge_service: KnowledgeService | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self.database = database
        self.city_repo = CityRepository(database) if database is not None else None
        self.knowledge_repo = KnowledgeRepository(database) if database is not None else None
        self.knowledge_service = knowledge_service or (
            KnowledgeService(self.knowledge_repo) if self.knowledge_repo is not None else None
        )
        self.llm_service = llm_service or LLMService()
        if agents is not None:
            self._agents = agents
        elif database is not None:
            self._agents = {
                "location": LocationAgent(database, knowledge_service=self.knowledge_service),
                "environment": EnvironmentAgent(database, knowledge_service=self.knowledge_service),
                "mobility": MobilityAgent(database, knowledge_service=self.knowledge_service),
                "cost_of_living": CostAgent(database, knowledge_service=self.knowledge_service),
                "accommodation": AccommodationAgent(database, knowledge_service=self.knowledge_service),
                "education_culture": EducationLifestyleAgent(database, knowledge_service=self.knowledge_service),
                "safety_healthcare": SafetyHealthcareAgent(database, knowledge_service=self.knowledge_service),
            }
        else:
            self._agents = {}

    def catalog(self) -> list[dict[str, str | bool]]:
        """Return catalog of available agents and their active configuration state."""
        return [
            {
                "agent_id": definition.agent_id,
                "display_name": definition.display_name,
                "scope": definition.scope,
                "configured": definition.agent_id in self._agents,
                "integration_status": "ready" if definition.agent_id in self._agents else definition.integration_status,
            }
            for definition in AGENT_CATALOG
        ]

    def resolve_city_id(self, query: str | None, explicit_city_id: str | None) -> str | None:
        """Resolve city identifier using explicit ID, exact match, alias resolution, or search."""
        if explicit_city_id:
            return explicit_city_id

        if not query or not self.city_repo:
            return None

        # Clean query text
        clean_text = re.sub(r"[^\w\s-]", "", query.strip())
        raw_tokens = [t.strip() for t in clean_text.split() if len(t.strip()) > 1]
        
        stop_words = {
            "what", "is", "the", "weather", "temperature", "and", "in", "to", "how", "tell",
            "me", "about", "of", "for", "a", "an", "cost", "live", "living", "should", "i",
            "move", "are", "can", "you", "does", "it", "have", "good", "bad", "like", "there",
            "will", "be", "with", "from", "at", "by", "this", "that", "my", "any", "which",
            "where", "when", "why", "who", "whom", "whose", "or", "if", "as", "into", "near",
            "commute", "transit", "safety", "crime", "education", "schools", "hospital",
            "healthcare", "rent", "cheap", "expensive", "afford", "overview", "compare",
            "ranking", "all", "general", "much", "many", "such", "some", "our", "your",
        }
        
        candidate_tokens = [t for t in raw_tokens if t.lower() not in stop_words and len(t) > 2]
        tokens = candidate_tokens if candidate_tokens else [t for t in raw_tokens if len(t) > 2]

        # 1. Direct query lookup as alias
        resolved = self.city_repo.resolve_alias_to_city_id(query.strip())
        if resolved:
            return resolved

        # 2. Check tokens against alias index
        for token in tokens:
            resolved_token = self.city_repo.resolve_alias_to_city_id(token)
            if resolved_token:
                return resolved_token

        # 3. Check search matches for query tokens
        for token in tokens:
            results, count = self.city_repo.search_cities(query=token, page=1, page_size=5)
            for city in results:
                name = (city.get("name") or "").lower()
                name_ascii = (city.get("name_ascii") or "").lower()
                token_lower = token.lower()
                if token_lower == name or token_lower == name_ascii:
                    return city["city_id"]

        # 4. Fallback search on full query string
        results, count = self.city_repo.search_cities(query=clean_text, page=1, page_size=1)
        if count > 0 and results:
            return results[0]["city_id"]

        return None

    def determine_relevant_agents(
        self,
        query: str | None = None,
        requested_agents: Sequence[str] | None = None,
    ) -> list[str]:
        """Determine which domain agents to execute via deterministic keyword routing."""
        all_catalog_ids = [d.agent_id for d in AGENT_CATALOG]

        # Explicit agent request takes precedence
        if requested_agents:
            valid_requested = [aid for aid in requested_agents if aid in all_catalog_ids]
            if valid_requested:
                return valid_requested

        if not query or not query.strip():
            return all_catalog_ids

        q_lower = query.lower()

        # Keyword mapping rules
        env_keywords = (
            "weather", "climate", "temperature", "rain", "monsoon", "humidity",
            "hot", "cold", "forecast", "sun", "cloud", "air", "aqi", "pollution",
            "smog", "pm2.5", "pm10", "clean air", "air quality", "environment",
        )
        cost_keywords = (
            "cost", "budget", "expensive", "afford", "affordability", "cheap",
            "living expense", "price", "prices", "fx", "currency", "exchange rate",
            "salary", "groceries", "restaurant",
        )
        mobility_keywords = (
            "transport", "transit", "metro", "bus", "train", "commute", "traffic",
            "drive", "route", "subway", "rail", "airport", "mobility", "flight",
        )
        education_keywords = (
            "university", "universities", "college", "colleges", "school", "schools",
            "education", "student", "students", "study", "academic", "ranking", "rankings",
            "campus", "culture", "lifestyle",
        )
        safety_keywords = (
            "hospital", "health", "healthcare", "doctor", "clinic", "emergency",
            "medical", "safe", "safety", "crime", "secure", "policing",
        )
        housing_keywords = (
            "rent", "apartment", "housing", "flat", "neighborhood", "locality",
            "area", "suburb", "district", "room", "stay", "accommodation",
        )
        relocation_keywords = (
            "move", "relocate", "relocation", "living in", "settle", "should i move",
            "overview", "compare", "city guide", "all", "general", "everything",
        )

        # Check relocation / general intent
        if any(term in q_lower for term in relocation_keywords):
            return all_catalog_ids

        selected: list[str] = []

        if any(term in q_lower for term in env_keywords):
            selected.append("environment")
        if any(term in q_lower for term in cost_keywords):
            selected.append("cost_of_living")
        if any(term in q_lower for term in mobility_keywords):
            selected.append("mobility")
        if any(term in q_lower for term in education_keywords):
            selected.append("education_culture")
        if any(term in q_lower for term in safety_keywords):
            selected.append("safety_healthcare")
        if any(term in q_lower for term in housing_keywords):
            if "accommodation" not in selected:
                selected.append("accommodation")
            if "location" not in selected:
                selected.append("location")

        # If no specific intent was detected, default to all 7 agents
        if not selected:
            return all_catalog_ids

        return selected

    async def execute_agents_async(
        self,
        request: AgentRequest,
        target_agent_ids: Sequence[str] | None = None,
    ) -> tuple[AgentResult, ...]:
        """Execute selected agents asynchronously."""
        results: list[AgentResult] = []
        target_ids = set(target_agent_ids) if target_agent_ids else {d.agent_id for d in AGENT_CATALOG}

        for definition in AGENT_CATALOG:
            if definition.agent_id not in target_ids:
                continue

            agent = self._agents.get(definition.agent_id)
            if agent is None:
                results.append(
                    AgentResult(
                        agent_id=definition.agent_id,
                        status=AgentStatus.UNAVAILABLE,
                        missing_data=("integration",),
                        unavailable_fields=("agent_service",),
                        detail="Agent not configured or database offline.",
                        summary="Agent unconfigured.",
                        confidence=0.0,
                    )
                )
                continue

            try:
                res = await agent.execute_async(request)
                results.append(res)
            except Exception as exc:
                results.append(
                    AgentResult(
                        agent_id=definition.agent_id,
                        status=AgentStatus.ERROR,
                        detail=f"Agent execution encountered error: {str(exc)}",
                        summary=f"Agent execution encountered error: {str(exc)}",
                        missing_data=("execution_error",),
                        unavailable_fields=("execution_error",),
                        warnings=(f"Execution failure: {str(exc)}",),
                        confidence=0.0,
                    )
                )

        return tuple(results)

    def execute_agents(
        self,
        request: AgentRequest,
        target_agent_ids: Sequence[str] | None = None,
    ) -> tuple[AgentResult, ...]:
        """Execute selected agents synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    asyncio.run,
                    self.execute_agents_async(request, target_agent_ids=target_agent_ids),
                ).result()
        return asyncio.run(self.execute_agents_async(request, target_agent_ids=target_agent_ids))

    async def synthesize_async(self, context: OrchestrationContext) -> AggregatedIntelligence:
        """Synthesize multi-agent outputs into explainable, structured intelligence."""
        city_id = self.resolve_city_id(context.query, context.city_id)

        if not city_id:
            unavailable_res = AgentResult(
                agent_id="location",
                status=AgentStatus.UNAVAILABLE,
                missing_data=("city_id",),
                unavailable_fields=("city_resolution",),
                detail="Could not resolve target city from request context or query.",
                summary="Target city could not be resolved.",
                confidence=0.0,
            )
            return AggregatedIntelligence(
                city_id=context.city_id or "unresolved",
                overall_status=AgentStatus.UNAVAILABLE,
                results=(unavailable_res,),
                all_sources=(),
                sources=(),
                selected_agents=(),
                signals=(),
                warnings=("Target city could not be resolved from input query.",),
                summary="Intelligence query could not be executed because no matching city was identified in canonical registry.",
                query=context.query,
            )

        selected_agents = self.determine_relevant_agents(
            query=context.query,
            requested_agents=context.target_agents or None,
        )

        agent_req = AgentRequest(city_id=city_id, query=context.query)
        results = await self.execute_agents_async(agent_req, target_agent_ids=selected_agents)

        # Retrieve canonical city overview for location grounding
        city_record: dict[str, Any] = {}
        if self.city_repo:
            found = self.city_repo.get_by_city_id(city_id)
            if found:
                city_record = {
                    "city_id": found.get("city_id"),
                    "name": found.get("name"),
                    "country_id": found.get("country_id"),
                    "country_iso2": found.get("country_iso2"),
                    "admin_name": found.get("admin_name"),
                    "population": found.get("population"),
                    "latitude": found.get("latitude"),
                    "longitude": found.get("longitude"),
                }

        # Aggregate sources, warnings, and unavailable fields
        all_sources: list[SourceProvenance] = []
        all_warnings: list[str] = []
        all_unavailable: list[str] = []
        seen_sources: set[str] = set()

        for r in results:
            for s in r.sources:
                key = f"{s.source_id}:{s.provider}"
                if key not in seen_sources:
                    seen_sources.add(key)
                    all_sources.append(s)
            all_warnings.extend(r.warnings)
            all_unavailable.extend(r.unavailable_fields)

        # Status determination
        statuses = [r.status for r in results]
        if all(s == AgentStatus.COMPLETE for s in statuses):
            overall = AgentStatus.COMPLETE
        elif any(s in (AgentStatus.COMPLETE, AgentStatus.PARTIAL, AgentStatus.FRESH, AgentStatus.DATABASE) for s in statuses):
            overall = AgentStatus.PARTIAL
        elif all(s == AgentStatus.ERROR for s in statuses):
            overall = AgentStatus.ERROR
        else:
            overall = AgentStatus.UNAVAILABLE

        # Extract structured signals deterministically
        signals: list[dict[str, Any]] = []
        summary_parts: list[str] = []

        city_name = city_record.get("name") or city_id
        country_code = city_record.get("country_iso2") or "Global"
        pop = city_record.get("population")
        pop_str = f"Pop: {pop:,}" if isinstance(pop, (int, float)) else "Pop: N/A"

        summary_parts.append(f"UrbanLens Grounded Report for {city_name} ({country_code}, {pop_str}).")

        for r in results:
            d = r.data
            if r.agent_id == "location" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "location",
                    "metric": "administrative_boundary",
                    "value": d.get("admin_name"),
                    "source": "canonical_city_registry",
                })
            elif r.agent_id == "environment" and r.status != AgentStatus.UNAVAILABLE:
                curr = d.get("current_weather") or {}
                if curr.get("temperature_c") is not None:
                    signals.append({
                        "domain": "environment",
                        "metric": "temperature_c",
                        "value": curr.get("temperature_c"),
                        "source": d.get("weather_meta", {}).get("provider", "weather"),
                    })
                aq = d.get("air_quality") or {}
                pollutants = aq.get("pollutants") or {}
                pm25 = pollutants.get("pm25") or (d.get("air_quality_global_weather") or {}).get("pm25")
                if pm25 is not None:
                    signals.append({
                        "domain": "environment",
                        "metric": "pm25_ug_m3",
                        "value": pm25,
                        "source": d.get("air_quality_meta", {}).get("provider", "air_quality"),
                    })
                if r.summary:
                    summary_parts.append(f"[Environment]: {r.summary}")
            elif r.agent_id == "cost_of_living" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "cost_of_living",
                    "metric": "basket_metrics_count",
                    "value": d.get("metrics_recorded_count", 0),
                    "source": "canonical_cost_dataset",
                })
                fx = d.get("live_exchange_rate")
                if fx:
                    signals.append({
                        "domain": "cost_of_living",
                        "metric": "fx_rate",
                        "value": f"1 USD = {fx.get('converted_amount')} {fx.get('to_currency')}",
                        "source": "frankfurter",
                    })
                if r.summary:
                    summary_parts.append(f"[Cost & Affordability]: {r.summary}")
            elif r.agent_id == "mobility" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "mobility",
                    "metric": "metropolitan_scale",
                    "value": d.get("metropolitan_scale"),
                    "source": "canonical_demographics",
                })
                signals.append({
                    "domain": "mobility",
                    "metric": "live_gtfs_connected",
                    "value": d.get("live_gtfs_connected"),
                    "source": "gtfs_provider",
                })
                if r.summary:
                    summary_parts.append(f"[Mobility]: {r.summary}")
            elif r.agent_id == "accommodation" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "accommodation",
                    "metric": "housing_metrics_count",
                    "value": d.get("housing_metrics_count", 0),
                    "source": "canonical_cost_dataset",
                })
                if r.summary:
                    summary_parts.append(f"[Accommodation]: {r.summary}")
            elif r.agent_id == "education_culture" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "education_culture",
                    "metric": "total_institutions",
                    "value": d.get("total_country_institutions", 0),
                    "source": "canonical_university_registry",
                })
                if r.summary:
                    summary_parts.append(f"[Education & Culture]: {r.summary}")
            elif r.agent_id == "safety_healthcare" and r.status != AgentStatus.UNAVAILABLE:
                signals.append({
                    "domain": "safety_healthcare",
                    "metric": "healthcare_facilities_count",
                    "value": d.get("healthcare_facilities_count", 0),
                    "source": "openstreetmap_overpass",
                })
                if r.summary:
                    summary_parts.append(f"[Safety & Healthcare]: {r.summary}")

        # Collect grounded knowledge evidence from agents
        collected_evidence: list[KnowledgeEvidence] = []
        for r in results:
            collected_evidence.extend(getattr(r, "knowledge_evidence", ()))

        # Also retrieve query-level knowledge evidence if query and service exist
        if context.query and self.knowledge_service:
            try:
                query_evidence = await self.knowledge_service.search_knowledge(
                    query=context.query,
                    city_id=city_id,
                    top_k=3,
                    min_score=0.1,
                )
                collected_evidence.extend(query_evidence)
            except Exception:
                pass

        # Deduplicate evidence by chunk_id and register source provenance
        unique_evidence: list[KnowledgeEvidence] = []
        seen_chunks: set[str] = set()
        for ev in collected_evidence:
            if ev.chunk_id not in seen_chunks:
                seen_chunks.add(ev.chunk_id)
                unique_evidence.append(ev)
                key = f"{ev.source}:knowledge"
                if key not in seen_sources:
                    seen_sources.add(key)
                    all_sources.append(
                        SourceProvenance(
                            source_id=ev.source,
                            provider="knowledge",
                            retrieved_at=ev.retrieved_at,
                            confidence=ev.retrieval_score or 1.0,
                        )
                    )

        if unique_evidence:
            sources_names = sorted(list(set(e.source for e in unique_evidence)))
            summary_parts.append(
                f"[Grounded Knowledge Evidence]: Found {len(unique_evidence)} documented reference(s) from {', '.join(sources_names)}."
            )

        summary_prefix = (
            f"UrbanLens intelligence synthesized across {len(results)} agent domains "
            f"with status '{overall.value}'. Total grounded sources: {len(all_sources)}."
        )
        deterministic_summary = f"{summary_prefix} " + " ".join(summary_parts)

        return AggregatedIntelligence(
            city_id=city_id,
            overall_status=overall,
            results=results,
            all_sources=tuple(all_sources),
            sources=tuple(all_sources),
            selected_agents=tuple(selected_agents),
            signals=tuple(signals),
            knowledge_evidence=tuple(unique_evidence),
            warnings=tuple(all_warnings),
            unavailable_fields=tuple(all_unavailable),
            location=city_record,
            summary=deterministic_summary,
            query=context.query,
        )

    def synthesize(self, context: OrchestrationContext) -> AggregatedIntelligence:
        """Synchronously synthesize multi-agent outputs into explainable intelligence."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.synthesize_async(context)).result()
        return asyncio.run(self.synthesize_async(context))

    async def ask_async(
        self,
        query: str,
        city_id: str | None = None,
    ) -> LLMAskResponse:
        """Execute multi-agent intelligence retrieval and synthesize grounded response via LLM reasoning."""
        context = OrchestrationContext(city_id=city_id, query=query)
        aggregated = await self.synthesize_async(context)
        return await self.llm_service.synthesize_grounded_answer(aggregated, query)

    def ask(
        self,
        query: str,
        city_id: str | None = None,
    ) -> LLMAskResponse:
        """Synchronously execute multi-agent retrieval and synthesize grounded response via LLM reasoning."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.ask_async(query, city_id=city_id)).result()
        return asyncio.run(self.ask_async(query, city_id=city_id))

