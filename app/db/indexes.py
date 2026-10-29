"""Index definitions and management corresponding to canonical collections."""

from typing import Any
from pymongo.database import Database
from app.core.logging import get_logger

logger = get_logger("db.indexes")

INDEX_DEFINITIONS: list[dict[str, Any]] = [
    {
        "collection": "cities",
        "keys": [("city_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"city_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "cities",
        "keys": [("worldcities_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"worldcities_id": {"$type": "number"}}},
    },
    {
        "collection": "cities",
        "keys": [("country_iso2", 1)],
        "options": {},
    },
    {
        "collection": "cities",
        "keys": [("latitude", 1), ("longitude", 1)],
        "options": {},
    },
    {
        "collection": "city_aliases",
        "keys": [("city_id", 1), ("normalized_alias", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "city_id": {"$type": "string", "$gt": ""},
                "normalized_alias": {"$type": "string", "$gt": ""},
            },
        },
    },
    {
        "collection": "city_provider_identities",
        "keys": [("provider", 1), ("provider_location_id", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "provider": {"$type": "string", "$gt": ""},
                "provider_location_id": {"$type": "string", "$gt": ""},
            },
        },
    },
    {
        "collection": "countries",
        "keys": [("country_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"country_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "countries",
        "keys": [("iso2", 1)],
        "options": {"unique": True, "partialFilterExpression": {"iso2": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "countries",
        "keys": [("iso3", 1)],
        "options": {"unique": True, "partialFilterExpression": {"iso3": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "country_metrics",
        "keys": [("country_id", 1), ("metric", 1), ("period", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "country_id": {"$type": "string", "$gt": ""},
                "metric": {"$type": "string", "$gt": ""},
                "period": {"$type": "number"},
            },
        },
    },
    {
        "collection": "gdp_country_metrics",
        "keys": [("country_id", 1), ("metric", 1), ("period", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "country_id": {"$type": "string", "$gt": ""},
                "metric": {"$type": "string", "$gt": ""},
                "period": {"$type": "number"},
            },
        },
    },
    {
        "collection": "cost_of_living",
        "keys": [("city_id", 1), ("metric", 1), ("observed_at", 1), ("source_id", 1), ("source_record_key", 1)],
        "options": {},
    },
    {
        "collection": "universities",
        "keys": [("university_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"university_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "university_rankings",
        "keys": [("university_id", 1), ("ranking_metric", 1), ("ranking_year", 1), ("source_record_key", 1)],
        "options": {},
    },
    {
        "collection": "weather_observations",
        "keys": [("city_id", 1), ("provider", 1), ("observed_at", 1), ("source_row", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "city_id": {"$type": "string", "$gt": ""},
                "provider": {"$type": "string", "$gt": ""},
                "observed_at": {"$type": "date"},
                "source_row": {"$type": "number"},
            },
        },
    },
    {
        "collection": "weather_forecasts_wmo",
        "keys": [("city_id", 1), ("provider", 1), ("forecast_for", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "city_id": {"$type": "string", "$gt": ""},
                "provider": {"$type": "string", "$gt": ""},
                "forecast_for": {"$type": "date"},
            },
        },
    },
    {
        "collection": "air_quality_observations_global_weather",
        "keys": [("city_id", 1), ("provider", 1), ("observed_at", 1), ("source_row", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "city_id": {"$type": "string", "$gt": ""},
                "provider": {"$type": "string", "$gt": ""},
                "observed_at": {"$type": "date"},
                "source_row": {"$type": "number"},
            },
        },
    },
    {
        "collection": "air_quality_observations_who",
        "keys": [("city_id", 1), ("source", 1), ("year", 1), ("source_row", 1)],
        "options": {
            "unique": True,
            "partialFilterExpression": {
                "city_id": {"$type": "string", "$gt": ""},
                "source": {"$type": "string", "$gt": ""},
                "year": {"$type": "number"},
                "source_row": {"$type": "number"},
            },
        },
    },
    {
        "collection": "source_registry",
        "keys": [("source_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"source_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "knowledge_documents",
        "keys": [("document_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"document_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "knowledge_documents",
        "keys": [("checksum", 1)],
        "options": {"unique": True, "partialFilterExpression": {"checksum": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "knowledge_documents",
        "keys": [("city_id", 1), ("category", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_documents",
        "keys": [("country_id", 1), ("category", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_documents",
        "keys": [("authority_tier", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("chunk_id", 1)],
        "options": {"unique": True, "partialFilterExpression": {"chunk_id": {"$type": "string", "$gt": ""}}},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("document_id", 1), ("chunk_index", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("city_id", 1), ("category", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("country_id", 1), ("category", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("scope", 1)],
        "options": {},
    },
    {
        "collection": "knowledge_chunks",
        "keys": [("authority_tier", 1)],
        "options": {},
    },
]


def ensure_indexes(database: Database) -> list[str]:
    """Ensure declared indexes exist without modifying documents."""
    results = []
    for spec in INDEX_DEFINITIONS:
        col_name = spec["collection"]
        keys = spec["keys"]
        options = spec.get("options", {})
        try:
            res = database[col_name].create_index(keys, **options)
            results.append(f"{col_name}: {res}")
        except Exception as exc:
            logger.warning("Could not apply index on %s: %s", col_name, exc)
    return results
