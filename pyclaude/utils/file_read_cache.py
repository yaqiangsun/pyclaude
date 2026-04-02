"""
File read cache utilities.

Cache file reads.
"""

from typing import Optional, Dict
import os
import time


class FileReadCache:
    """Cache for file reads."""

    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple] = {}  # path -> (content, timestamp)

    def get(self, path: str) -> Optional[str]:
        """Get cached file content.

        Args:
            path: File path

        Returns:
            Content or None if not cached
        """
        if path not in self._cache:
            return None

        content, timestamp = self._cache[path]
        if time.time() - timestamp > self.ttl:
            del self._cache[path]
            return None

        return content

    def set(self, path: str, content: str) -> None:
        """Cache file content.

        Args:
            path: File path
            content: File content
        """
        self._cache[path] = (content, time.time())

    def invalidate(self, path: str) -> None:
        """Invalidate cached content.

        Args:
            path: File path
        """
        self._cache.pop(path, None)

    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()


# Global cache
_file_read_cache = FileReadCache()


def get_file_read_cache() -> FileReadCache:
    """Get global file read cache."""
    return _file_read_cache


__all__ = [
    "FileReadCache",
    "get_file_read_cache",
]