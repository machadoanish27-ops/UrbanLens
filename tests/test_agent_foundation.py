import unittest

from app.agents.catalog import AGENT_CATALOG
from app.models.agent import AgentRequest, AgentStatus
from app.services.data_freshness import freshness_status
from app.services.orchestrator import AgentOrchestrator
from datetime import datetime, timedelta, timezone


class AgentFoundationTests(unittest.TestCase):
    def test_catalog_has_seven_unconfigured_capabilities(self) -> None:
        catalog = AgentOrchestrator().catalog()
        self.assertEqual(len(AGENT_CATALOG), 7)
        self.assertEqual(len(catalog), 7)
        self.assertTrue(all(not item["configured"] for item in catalog))

    def test_unconfigured_agents_return_explicit_status(self) -> None:
        results = AgentOrchestrator().execute(AgentRequest(city_id="city_example"))
        self.assertEqual(len(results), 7)
        self.assertTrue(all(result.status is AgentStatus.UNAVAILABLE for result in results))
        self.assertTrue(all(result.detail and "TODO" in result.detail for result in results))

    def test_freshness_distinguishes_missing_and_stale_data(self) -> None:
        now = datetime.now(timezone.utc)
        self.assertIs(freshness_status(None, timedelta(hours=1), now), AgentStatus.UNAVAILABLE)
        self.assertIs(
            freshness_status(now - timedelta(days=2), timedelta(hours=1), now),
            AgentStatus.STALE,
        )


if __name__ == "__main__":
    unittest.main()