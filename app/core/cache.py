"""Production-grade multi-backend caching system with Redis, In-Memory fallback, and stale-while-revalidate capabilities."""

from __future__ import annotations

import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.core.config import settings

logger = logging.getLogger("app.core.cache")

ALLOWED_NAMESPACES: frozenset[str] = frozenset({
    "weather",
    "air_quality",
    "currency",
    "geocoding",
    "routing",
    "places",
    "transit",
    "education",
    "healthcare",
    "knowledge",
    "llm",
    "general",
})


@dataclass(frozen=True)
class CacheEntry:
    """Wrapped cache entry carrying value, timestamps, and staleness metadata."""

    value: Any
    created_at: float
    expires_at: float
    is_stale: bool
    age_seconds: float


class BaseCacheBackend(ABC):
    """Abstract interface defining required cache backend operations."""

    @abstractmethod
    def get(self, key: str, allow_stale: bool = False) -> Any | None:
        """Retrieve value from cache. If allow_stale is True, returns expired value if available."""
        ...

    @abstractmethod
    def get_entry(self, key: str, allow_stale: bool = False) -> CacheEntry | None:
        """Retrieve wrapped CacheEntry with freshness/staleness metadata."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        """Store value with TTL. Values of None must be ignored."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Evict all entries from this backend."""
        ...

    @abstractmethod
    def size(self) -> int:
        """Return number of active non-expired entries."""
        ...

    @abstractmethod
    def is_healthy(self) -> bool:
        """Return whether backend is reachable and functioning."""
        ...


class InMemoryCacheBackend(BaseCacheBackend):
    """Thread-safe in-memory cache supporting TTL, stale reads, and safe cleanup."""

    def __init__(
        self,
        default_ttl_seconds: float = 300.0,
        stale_multiplier: float = 4.0,
    ) -> None:
        self.default_ttl = float(default_ttl_seconds)
        self.stale_multiplier = max(1.0, float(stale_multiplier))
        # key -> (value, expires_at, created_at, purge_at)
        self._store: dict[str, tuple[Any, float, float, float]] = {}
        self._lock = threading.RLock()

    def get(self, key: str, allow_stale: bool = False) -> Any | None:
        entry = self.get_entry(key, allow_stale=allow_stale)
        return entry.value if entry is not None else None

    def get_entry(self, key: str, allow_stale: bool = False) -> CacheEntry | None:
        now = time.time()
        with self._lock:
            stored = self._store.get(key)
            if stored is None:
                return None
            val, expires_at, created_at, purge_at = stored

            # If past maximum purge window, evict immediately
            if now > purge_at:
                del self._store[key]
                return None

            is_expired = now > expires_at
            if is_expired and not allow_stale:
                return None

            return CacheEntry(
                value=val,
                created_at=created_at,
                expires_at=expires_at,
                is_stale=is_expired,
                age_seconds=max(0.0, now - created_at),
            )

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        if value is None:
            return
        ttl = float(ttl_seconds if ttl_seconds is not None else self.default_ttl)
        now = time.time()
        expires_at = now + ttl
        purge_at = now + (ttl * self.stale_multiplier)

        with self._lock:
            self._store[key] = (value, expires_at, now, purge_at)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def cleanup(self) -> int:
        """Evict all items past their purge window."""
        now = time.time()
        with self._lock:
            to_remove = [k for k, (_, _, _, purge_at) in self._store.items() if now > purge_at]
            for k in to_remove:
                del self._store[k]
            return len(to_remove)

    def size(self) -> int:
        now = time.time()
        with self._lock:
            return sum(1 for _, expires_at, _, _ in self._store.values() if now <= expires_at)

    def is_healthy(self) -> bool:
        return True


class RedisCacheBackend(BaseCacheBackend):
    """Production Redis cache backend with resilient error handling and graceful offline fallback."""

    def __init__(
        self,
        redis_url: str | None = None,
        default_ttl_seconds: float = 300.0,
        stale_multiplier: float = 4.0,
        connect_timeout_ms: int = 1500,
        socket_timeout_ms: int = 1500,
    ) -> None:
        self.redis_url = redis_url or settings.REDIS_URL
        self.default_ttl = float(default_ttl_seconds)
        self.stale_multiplier = max(1.0, float(stale_multiplier))
        self.connect_timeout_ms = connect_timeout_ms
        self.socket_timeout_ms = socket_timeout_ms
        self._client: Any = None
        self._is_available: bool = False
        self._last_error: str | None = None
        self._init_client()

    def _init_client(self) -> None:
        if not self.redis_url:
            self._is_available = False
            return
        try:
            import redis

            self._client = redis.Redis.from_url(
                self.redis_url,
                socket_connect_timeout=self.connect_timeout_ms / 1000.0,
                socket_timeout=self.socket_timeout_ms / 1000.0,
                decode_responses=True,
            )
            # Test connectivity with ping
            self._client.ping()
            self._is_available = True
            self._last_error = None
            logger.info("Connected successfully to Redis at %s", settings.safe_redis_url)
        except Exception as exc:
            self._is_available = False
            self._last_error = str(exc)
            logger.warning("Redis backend unavailable (%s). Falling back to in-memory cache.", exc)

    def is_healthy(self) -> bool:
        if not self.redis_url or not self._is_available or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            self._is_available = False
            return False

    def get(self, key: str, allow_stale: bool = False) -> Any | None:
        entry = self.get_entry(key, allow_stale=allow_stale)
        return entry.value if entry is not None else None

    def get_entry(self, key: str, allow_stale: bool = False) -> CacheEntry | None:
        if not self.is_healthy():
            return None
        try:
            raw = self._client.get(key)
            if not raw:
                return None
            doc = json.loads(raw)
            val = doc.get("v")
            created_at = float(doc.get("c", 0.0))
            expires_at = float(doc.get("e", 0.0))
            now = time.time()

            is_expired = now > expires_at
            if is_expired and not allow_stale:
                return None

            return CacheEntry(
                value=val,
                created_at=created_at,
                expires_at=expires_at,
                is_stale=is_expired,
                age_seconds=max(0.0, now - created_at),
            )
        except Exception as exc:
            logger.warning("Redis GET error for key %s: %s", key, exc)
            self._is_available = False
            return None

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        if value is None or not self.is_healthy():
            return
        ttl = float(ttl_seconds if ttl_seconds is not None else self.default_ttl)
        now = time.time()
        expires_at = now + ttl
        raw_doc = {
            "v": value,
            "c": now,
            "e": expires_at,
        }
        # Keep key in Redis up to stale multiplier window
        redis_ttl = int(ttl * self.stale_multiplier)
        try:
            payload = json.dumps(raw_doc, default=str)
            self._client.setex(key, redis_ttl, payload)
        except Exception as exc:
            logger.warning("Redis SET error for key %s: %s", key, exc)
            self._is_available = False

    def delete(self, key: str) -> bool:
        if not self.is_healthy():
            return False
        try:
            return bool(self._client.delete(key))
        except Exception as exc:
            logger.warning("Redis DELETE error: %s", exc)
            self._is_available = False
            return False

    def clear(self) -> None:
        if not self.is_healthy():
            return
        try:
            # Delete urbanlens prefixed keys only
            keys = self._client.keys("urbanlens:*")
            if keys:
                self._client.delete(*keys)
        except Exception as exc:
            logger.warning("Redis CLEAR error: %s", exc)
            self._is_available = False

    def size(self) -> int:
        if not self.is_healthy():
            return 0
        try:
            return len(self._client.keys("urbanlens:*"))
        except Exception:
            return 0


class CacheService:
    """Unified caching service combining Redis, in-memory local fallback, and namespace isolation."""

    def __init__(
        self,
        default_ttl_seconds: float | None = None,
        redis_url: str | None = None,
        enable_redis: bool | None = None,
    ) -> None:
        self.default_ttl = float(
            default_ttl_seconds
            if default_ttl_seconds is not None
            else settings.CACHE_DEFAULT_TTL_SECONDS
        )
        self.enable_redis = (
            enable_redis
            if enable_redis is not None
            else (settings.REDIS_ENABLED or bool(settings.REDIS_URL))
        )

        self.local_backend = InMemoryCacheBackend(
            default_ttl_seconds=self.default_ttl,
            stale_multiplier=settings.CACHE_STALE_TTL_MULTIPLIER,
        )

        self.redis_backend: RedisCacheBackend | None = None
        if self.enable_redis:
            self.redis_backend = RedisCacheBackend(
                redis_url=redis_url,
                default_ttl_seconds=self.default_ttl,
                stale_multiplier=settings.CACHE_STALE_TTL_MULTIPLIER,
                connect_timeout_ms=settings.REDIS_CONNECT_TIMEOUT_MS,
                socket_timeout_ms=settings.REDIS_SOCKET_TIMEOUT_MS,
            )

    @property
    def is_redis_available(self) -> bool:
        return self.redis_backend is not None and self.redis_backend.is_healthy()

    def get(self, key: str, allow_stale: bool = False) -> Any | None:
        """Retrieve value from cache with automatic Redis -> in-memory fallback."""
        # 1. Try Redis backend if active
        if self.is_redis_available and self.redis_backend:
            val = self.redis_backend.get(key, allow_stale=allow_stale)
            if val is not None:
                return val

        # 2. Fall back to local in-memory backend
        return self.local_backend.get(key, allow_stale=allow_stale)

    def get_entry(self, key: str, allow_stale: bool = False) -> CacheEntry | None:
        """Retrieve wrapped CacheEntry with staleness metadata."""
        if self.is_redis_available and self.redis_backend:
            entry = self.redis_backend.get_entry(key, allow_stale=allow_stale)
            if entry is not None:
                return entry

        return self.local_backend.get_entry(key, allow_stale=allow_stale)

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        """Store value into both local in-memory cache and Redis if available."""
        if value is None:
            return
        # Store locally first
        self.local_backend.set(key, value, ttl_seconds=ttl_seconds)

        # Replicate to Redis if active
        if self.is_redis_available and self.redis_backend:
            self.redis_backend.set(key, value, ttl_seconds=ttl_seconds)

    def delete(self, key: str) -> bool:
        """Delete key across all active backends."""
        deleted_local = self.local_backend.delete(key)
        deleted_redis = False
        if self.is_redis_available and self.redis_backend:
            deleted_redis = self.redis_backend.delete(key)
        return deleted_local or deleted_redis

    def clear(self) -> None:
        """Clear cache across all backends."""
        self.local_backend.clear()
        if self.is_redis_available and self.redis_backend:
            self.redis_backend.clear()

    def cleanup(self) -> int:
        """Evict expired purge entries from local cache."""
        return self.local_backend.cleanup()

    def size(self) -> int:
        """Return total active entries."""
        if self.is_redis_available and self.redis_backend:
            return self.redis_backend.size()
        return self.local_backend.size()

    def get_diagnostics(self) -> dict[str, Any]:
        """Return operational cache diagnostics for health monitoring."""
        return {
            "redis_enabled": self.enable_redis,
            "redis_connected": self.is_redis_available,
            "active_backend": "redis" if self.is_redis_available else "in_memory",
            "in_memory_entries": self.local_backend.size(),
            "default_ttl_seconds": self.default_ttl,
            "stale_multiplier": settings.CACHE_STALE_TTL_MULTIPLIER,
            "redis_url_configured": bool(settings.REDIS_URL),
        }


def build_cache_key(namespace: str, **kwargs: Any) -> str:
    """Construct deterministic cache key with namespace prefix and sorted argument pairs."""
    clean_ns = namespace.strip().lower()
    sorted_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
    return f"urbanlens:{clean_ns}:{':'.join(sorted_parts)}"


# Backward-compatibility alias for existing code
class InMemoryTTLCache(InMemoryCacheBackend):
    """Backward-compatible alias of InMemoryCacheBackend."""

    pass


# Global default service cache singleton
service_cache: CacheService = CacheService()
