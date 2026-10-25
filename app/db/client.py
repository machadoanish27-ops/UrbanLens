"""MongoDB client connection manager and health check utilities."""

import time
from typing import Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError

from app.core.config import settings
from app.core.exceptions import DatabaseUnavailableException
from app.core.logging import get_logger

try:
    import certifi
    DEFAULT_TLS_CA_FILE = certifi.where()
except ImportError:
    DEFAULT_TLS_CA_FILE = None

logger = get_logger("db.client")


class MongoClientManager:
    """Manages the MongoDB Atlas client singleton lifecycle."""

    _client: MongoClient | None = None
    _db: Database | None = None

    @classmethod
    def initialize_client(cls, uri: str | None = None, database_name: str | None = None) -> MongoClient:
        """Initialize or return the existing MongoClient singleton."""
        if cls._client is not None:
            return cls._client

        connection_uri = uri or settings.MONGODB_URI
        if not connection_uri:
            logger.warning("No MONGODB_URI configured in environment.")
            raise DatabaseUnavailableException("MONGODB_URI is not configured.")

        tls_options: dict[str, Any] = {}
        if DEFAULT_TLS_CA_FILE and connection_uri.startswith("mongodb+srv://"):
            tls_options["tlsCAFile"] = DEFAULT_TLS_CA_FILE

        logger.info("Initializing MongoDB client for cluster...")
        try:
            cls._client = MongoClient(
                connection_uri,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                **tls_options,
            )
            return cls._client
        except Exception as exc:
            logger.error("Failed to construct MongoDB client: %s", str(exc))
            raise DatabaseUnavailableException(f"Failed to initialize database client: {str(exc)}") from exc

    @classmethod
    def get_database(cls, db_name: str | None = None) -> Database:
        """Return the target Database instance."""
        target_name = db_name or settings.MONGODB_DB
        client = cls.initialize_client()
        return client[target_name]

    @classmethod
    def check_health(cls, timeout_ms: int = 3000) -> dict[str, Any]:
        """Perform a ping command to evaluate MongoDB availability without exposing credentials."""
        start_time = time.perf_counter()
        db_name = settings.MONGODB_DB
        try:
            client = cls.initialize_client()
            # Perform ping with strict timeout
            client.admin.command("ping")
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "healthy",
                "database": db_name,
                "latency_ms": latency_ms,
                "connected": True,
            }
        except (ServerSelectionTimeoutError, ConnectionFailure) as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("MongoDB ping failed (timeout/connection failure): %s", str(exc))
            return {
                "status": "unhealthy",
                "database": db_name,
                "latency_ms": latency_ms,
                "connected": False,
                "error": "Database unreachable or server selection timed out",
            }
        except PyMongoError as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("MongoDB ping error: %s", str(exc))
            return {
                "status": "unhealthy",
                "database": db_name,
                "latency_ms": latency_ms,
                "connected": False,
                "error": "Database operation error",
            }
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("MongoDB client initialization error: %s", str(exc))
            return {
                "status": "unhealthy",
                "database": db_name,
                "latency_ms": latency_ms,
                "connected": False,
                "error": "Database configuration or network error",
            }

    @classmethod
    def close(cls) -> None:
        """Close client connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed.")


def get_db() -> Database:
    """FastAPI dependency for accessing the database."""
    return MongoClientManager.get_database()
