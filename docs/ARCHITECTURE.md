# Architecture

## Application

`app/models/` defines city/provider identities and agent request, result, status, and provenance contracts. `app/agents/catalog.py` names the seven planned domains. No domain agent is configured yet. `AgentOrchestrator` accepts injected implementations and returns explicit unavailable results for integrations that are absent.

`app/api/` currently exposes health and agent-discovery routes only. `app/services/data_freshness.py` distinguishes unavailable, current, and stale observations. `app/db/settings.py` validates the required environment settings but does not open a connection. API/database integrations remain configurable.

## Data and ETL

Canonical city IDs are stable UrbanLens IDs. Provider location IDs remain scoped by provider. Source records retain provenance, observation/retrieval time, and source version when present. Semantic nulls stay missing, quarantines stay separate, and negative values are not globally rejected.

The MongoDB importer preflights source keys, batches upserts, checkpoints after successful batches, and reports CSV versus database counts. Weather observation writes are insert-only to preserve the partially imported historical set. The scripts in `scripts/` validate local data or perform read-only MongoDB checks; index setup is separate.

## Seven agent domains

Location / City Intelligence; Environment / Climate; Mobility / Transportation; Cost-of-Living / Budget; Accommodation / Locality; Education / Culture / Lifestyle; Safety / Healthcare / Essential Information. These are interfaces/capabilities only; provider-specific behavior is TODO until configured.