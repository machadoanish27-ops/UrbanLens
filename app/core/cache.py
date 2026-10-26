"""In-memory TTL cache for service-layer caching of live provider responses."""

import threading
import time
from typing import Any


class InMemoryTTLCache:
    """Thread-safe in-memory cache with per-item and default TTL expiration."""

    def __init__(self, default_ttl_seconds: float = 300.0) -> None:
        self.default_ttl = float(default_ttl_seconds)
        self._store: dict[str, tuple[Any, float, float]] = {}  # key -> (value, expires_at, created_at)
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """Retrieve value from cache if present and not expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at, _ = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        """Store value with TTL. Does not cache None."""
        if value is None:
            return
        ttl = float(ttl_seconds if ttl_seconds is not None else self.default_ttl)
        now = time.time()
        expires_at = now + ttl
        with self._lock:
            self._store[key] = (value, expires_at, now)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._store.clear()

    def cleanup(self) -> int:
        """Evict all expired entries and return number of evicted items."""
        now = time.time()
        with self._lock:
            expired_keys = [k for k, (_, expires_at, _) in self._store.items() if now > expires_at]
            for k in expired_keys:
                del self._store[k]
            return len(expired_keys)

    def size(self) -> int:
        """Return number of currently active non-expired entries."""
        now = time.time()
        with self._lock:
            return sum(1 for _, expires_at, _ in self._store.values() if now <= expires_at)


def build_cache_key(namespace: str, **kwargs: Any) -> str:
    """Construct deterministic cache key from namespace and sorted parameter arguments."""
    sorted_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
    return f"{namespace}:{':'.join(sorted_parts)}"


# Global default service cache instance
service_cache = InMemoryTTLCache(default_ttl_seconds=300.0)
