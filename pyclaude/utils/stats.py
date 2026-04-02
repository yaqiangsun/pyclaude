"""
Stats utilities.

Statistics tracking and reporting.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class StatEntry:
    """A statistics entry."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)


class StatsTracker:
    """Track various statistics."""

    def __init__(self):
        self.stats: List[StatEntry] = []

    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a stat.

        Args:
            name: Stat name
            value: Stat value
            tags: Optional tags
        """
        self.stats.append(StatEntry(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
        ))

    def get(self, name: str) -> List[StatEntry]:
        """Get stats by name.

        Args:
            name: Stat name

        Returns:
            List of stat entries
        """
        return [s for s in self.stats if s.name == name]

    def get_latest(self, name: str) -> Optional[StatEntry]:
        """Get latest stat by name.

        Args:
            name: Stat name

        Returns:
            Latest stat or None
        """
        stats = self.get(name)
        return stats[-1] if stats else None

    def clear(self) -> None:
        """Clear all stats."""
        self.stats.clear()


# Global tracker
_stats_tracker = StatsTracker()


def get_stats_tracker() -> StatsTracker:
    """Get global stats tracker."""
    return _stats_tracker


def record_stat(name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Record a stat to global tracker."""
    _stats_tracker.record(name, value, tags)


__all__ = [
    "StatEntry",
    "StatsTracker",
    "get_stats_tracker",
    "record_stat",
]