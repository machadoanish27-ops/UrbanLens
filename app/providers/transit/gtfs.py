"""GTFS and GTFS-Realtime public transport provider implementation."""

from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.transit.base import (
    BaseTransitProvider,
    NormalizedTransitAlert,
    NormalizedTransitFeedInfo,
)

logger = get_logger("providers.transit.gtfs")


class GTFSTransitProvider(BaseTransitProvider):
    """Replaceable transit provider for GTFS schedule and GTFS-Realtime feeds.
    
    UrbanLens explicitly acknowledges that public transit data is federated by local transit
    authorities and does not possess a single universal global API. Feeds must be explicitly
    configured per city or metropolitan agency.
    """

    def __init__(
        self,
        configured_feeds: dict[str, dict[str, Any]] | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.configured_feeds = configured_feeds if configured_feeds is not None else {}
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "gtfs"

    @property
    def source_info(self) -> str:
        return "GTFS/GTFS-Realtime Federated Agency Feeds"

    async def get_transit_info(self, city_id: str) -> ProviderResponse[NormalizedTransitFeedInfo]:
        """Fetch GTFS metadata or return explicit DATA_UNAVAILABLE when unconfigured."""
        feed_config = self.configured_feeds.get(city_id)

        if not feed_config:
            logger.info("No GTFS feed configured for city '%s'. Returning explicit DATA_UNAVAILABLE.", city_id)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail=f"No GTFS transit feed is configured for city '{city_id}'. Universal global coverage is not claimed.",
                ),
                data=NormalizedTransitFeedInfo(
                    city_id=city_id,
                    is_feed_configured=False,
                    coverage_summary="Public transit feed not registered for this metropolitan area.",
                ),
            )

        # Configured feed processing
        agency = feed_config.get("agency_name", "Local Transit Authority")
        feed_url = feed_config.get("feed_url")
        rt_url = feed_config.get("realtime_url")
        routes_count = feed_config.get("routes_count")

        raw_alerts = feed_config.get("alerts", [])
        alerts = [
            NormalizedTransitAlert(
                id=str(a.get("id", i)),
                cause=a.get("cause"),
                effect=a.get("effect"),
                header_text=a.get("header_text", "Service notice"),
                description_text=a.get("description_text"),
            )
            for i, a in enumerate(raw_alerts)
        ]

        normalized = NormalizedTransitFeedInfo(
            city_id=city_id,
            is_feed_configured=True,
            agency_name=agency,
            feed_url=feed_url,
            realtime_url=rt_url,
            coverage_summary=f"Active GTFS feed registered for {agency}.",
            routes_count=routes_count,
            alerts=alerts,
        )

        return ProviderResponse(
            meta=self.create_meta(status=LiveStatus.FRESH),
            data=normalized,
        )
