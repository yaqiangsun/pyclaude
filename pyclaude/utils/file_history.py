"""
File history utilities.

Tracks file access history.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileAccess:
    """File access record."""
    path: str
    timestamp: datetime
    operation: str  # read, write, edit


class FileHistory:
    """Tracks file access history."""

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.accesses: List[FileAccess] = []

    def record_access(
        self,
        path: str,
        operation: str,
    ) -> None:
        """Record a file access.

        Args:
            path: File path
            operation: Operation type
        """
        self.accesses.append(FileAccess(
            path=path,
            timestamp=datetime.now(),
            operation=operation,
        ))
        # Trim if needed
        if len(self.accesses) > self.max_entries:
            self.accesses = self.accesses[-self.max_entries:]

    def get_recent(self, limit: int = 10) -> List[FileAccess]:
        """Get recent file accesses.

        Args:
            limit: Maximum entries

        Returns:
            Recent accesses
        """
        return self.accesses[-limit:]

    def get_by_path(self, path: str) -> List[FileAccess]:
        """Get accesses for a specific path.

        Args:
            path: File path

        Returns:
            Access records
        """
        return [a for a in self.accesses if a.path == path]


# Global history
_file_history = FileHistory()


def get_file_history() -> FileHistory:
    """Get global file history."""
    return _file_history


def record_file_access(path: str, operation: str) -> None:
    """Record file access to global history."""
    _file_history.record_access(path, operation)


__all__ = [
    "FileAccess",
    "FileHistory",
    "get_file_history",
    "record_file_access",
]