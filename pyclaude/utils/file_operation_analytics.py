"""
File operation analytics.

Track file operation statistics.
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FileOperationStats:
    """File operation statistics."""
    reads: int = 0
    writes: int = 0
    edits: int = 0
    deletes: int = 0
    last_operation: datetime = field(default_factory=datetime.now)


class FileOperationAnalytics:
    """Track file operation analytics."""

    def __init__(self):
        self._stats: Dict[str, FileOperationStats] = {}

    def record_read(self, path: str) -> None:
        """Record a read operation."""
        self._get_stats(path).reads += 1

    def record_write(self, path: str) -> None:
        """Record a write operation."""
        self._stats[path].writes += 1

    def record_edit(self, path: str) -> None:
        """Record an edit operation."""
        self._stats[path].edits += 1

    def record_delete(self, path: str) -> None:
        """Record a delete operation."""
        self._get_stats(path).deletes += 1

    def _get_stats(self, path: str) -> FileOperationStats:
        """Get stats for path."""
        if path not in self._stats:
            self._stats[path] = FileOperationStats()
        return self._stats[path]


# Global analytics
_analytics = FileOperationAnalytics()


def get_file_operation_analytics() -> FileOperationAnalytics:
    """Get global analytics."""
    return _analytics


__all__ = [
    "FileOperationStats",
    "FileOperationAnalytics",
    "get_file_operation_analytics",
]