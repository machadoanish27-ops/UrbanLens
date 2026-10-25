"""Source registry repository accessing source metadata and provenance definitions."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class SourceRegistryRepository(BaseRepository):
    """Repository for source registry records."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "source_registry")

    def get_by_source_id(self, source_id: str) -> dict[str, Any] | None:
        """Fetch metadata for a given source ID."""
        return self.find_one({"source_id": source_id})
