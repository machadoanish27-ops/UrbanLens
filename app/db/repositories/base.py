"""Base repository providing standardized MongoDB queries, pagination, and projection."""

from typing import Any, Mapping, Sequence
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.core.exceptions import DatabaseUnavailableException
from app.core.logging import get_logger

logger = get_logger("db.repository")


def clean_mongo_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Recursively convert ObjectIds and non-serializable BSON types to standard Python primitives."""
    if doc is None:
        return None
    cleaned = {}
    for key, val in doc.items():
        if key == "_id" and isinstance(val, ObjectId):
            cleaned["id"] = str(val)
        elif isinstance(val, ObjectId):
            cleaned[key] = str(val)
        elif isinstance(val, dict):
            cleaned[key] = clean_mongo_doc(val)
        elif isinstance(val, list):
            cleaned[key] = [clean_mongo_doc(item) if isinstance(item, dict) else item for item in val]
        else:
            cleaned[key] = val
    return cleaned


class BaseRepository:
    """Base repository class with common query helpers and pagination."""

    def __init__(self, database: Database, collection_name: str) -> None:
        self.database = database
        self.collection_name = collection_name

    @property
    def collection(self) -> Collection:
        return self.database[self.collection_name]

    def find_one(
        self,
        query: Mapping[str, Any],
        projection: Mapping[str, Any] | Sequence[str] | None = None,
        sort: Sequence[tuple[str, int]] | None = None,
    ) -> dict[str, Any] | None:
        """Find a single document matching query."""
        try:
            cursor = self.collection.find(query, projection)
            if sort:
                cursor = cursor.sort(sort)
            raw = next(cursor, None)
            return clean_mongo_doc(raw)
        except PyMongoError as exc:
            logger.error("MongoDB query failure in %s: %s", self.collection_name, exc)
            raise DatabaseUnavailableException(str(exc)) from exc

    def find_many(
        self,
        query: Mapping[str, Any] | None = None,
        projection: Mapping[str, Any] | Sequence[str] | None = None,
        sort: Sequence[tuple[str, int]] | None = None,
        limit: int | None = None,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        """Find multiple documents matching query."""
        filter_dict = query or {}
        try:
            cursor = self.collection.find(filter_dict, projection)
            if sort:
                cursor = cursor.sort(sort)
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit is not None and limit > 0:
                cursor = cursor.limit(limit)
            return [clean_mongo_doc(doc) for doc in cursor]
        except PyMongoError as exc:
            logger.error("MongoDB find_many failure in %s: %s", self.collection_name, exc)
            raise DatabaseUnavailableException(str(exc)) from exc

    def count(self, query: Mapping[str, Any] | None = None) -> int:
        """Count documents matching query."""
        filter_dict = query or {}
        try:
            return self.collection.count_documents(filter_dict)
        except PyMongoError as exc:
            logger.error("MongoDB count failure in %s: %s", self.collection_name, exc)
            raise DatabaseUnavailableException(str(exc)) from exc

    def find_paginated(
        self,
        query: Mapping[str, Any] | None = None,
        sort: Sequence[tuple[str, int]] | None = None,
        page: int = 1,
        page_size: int = 20,
        projection: Mapping[str, Any] | Sequence[str] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return (items, total_count) for pagination."""
        filter_dict = query or {}
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        skip = (page - 1) * page_size
        try:
            total = self.collection.count_documents(filter_dict)
            items = self.find_many(filter_dict, projection=projection, sort=sort, limit=page_size, skip=skip)
            return items, total
        except PyMongoError as exc:
            logger.error("MongoDB find_paginated failure in %s: %s", self.collection_name, exc)
            raise DatabaseUnavailableException(str(exc)) from exc
