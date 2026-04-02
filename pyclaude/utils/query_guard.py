"""
Query guard utilities.

Prevents duplicate or rapid-fire queries to external services.
"""

import time
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class QueryGuard:
    """Guard to prevent duplicate queries."""

    _last_query: Optional[str] = None
    _last_result: Optional[Any] = None
    _last_query_time: float = 0
    _cache_ttl_ms: int = 1000  # 1 second default TTL

    def can_query(self, query: str) -> bool:
        """Check if query should be executed.

        Args:
            query: The query string

        Returns:
            True if query should execute (not duplicate)
        """
        now = time.time() * 1000

        # Different query or cache expired
        if query != self._last_query:
            return True

        if now - self._last_query_time > self._cache_ttl_ms:
            return True

        return False

    def record_query(self, query: str, result: Any) -> None:
        """Record a query and its result.

        Args:
            query: The query string
            result: The query result
        """
        self._last_query = query
        self._last_result = result
        self._last_query_time = time.time() * 1000

    def get_cached_result(self, query: str) -> Optional[Any]:
        """Get cached result for query.

        Args:
            query: The query string

        Returns:
            Cached result or None
        """
        if query == self._last_query:
            now = time.time() * 1000
            if now - self._last_query_time <= self._cache_ttl_ms:
                return self._last_result
        return None

    def set_ttl(self, ttl_ms: int) -> None:
        """Set cache TTL in milliseconds."""
        self._cache_ttl_ms = ttl_ms


# Global query guard instance
_default_query_guard = QueryGuard()


def get_query_guard() -> QueryGuard:
    """Get the default query guard instance."""
    return _default_query_guard


def can_query(query: str) -> bool:
    """Check if query can be executed using default guard."""
    return _default_query_guard.can_query(query)


def record_query(query: str, result: Any) -> None:
    """Record query result using default guard."""
    _default_query_guard.record_query(query, result)


def get_cached_result(query: str) -> Optional[Any]:
    """Get cached result using default guard."""
    return _default_query_guard.get_cached_result(query)


__all__ = [
    "QueryGuard",
    "get_query_guard",
    "can_query",
    "record_query",
    "get_cached_result",
]