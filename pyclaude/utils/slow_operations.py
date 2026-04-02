"""
Slow operations utilities.

Track slow operations.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SlowOperation:
    """A slow operation record."""
    name: str
    duration_ms: float
    timestamp: float


class SlowOperationsTracker:
    """Track slow operations."""

    def __init__(self, threshold_ms: float = 1000):
        self.threshold_ms = threshold_ms
        self._operations: List[SlowOperation] = []

    def record(self, name: str, duration_ms: float) -> None:
        """Record an operation."""
        if duration_ms >= self.threshold_ms:
            self._operations.append(SlowOperation(
                name=name,
                duration_ms=duration_ms,
                timestamp=time.time(),
            ))

    def get_slow_operations(self) -> List[SlowOperation]:
        """Get slow operations."""
        return self._operations


_tracker = SlowOperationsTracker()


def get_slow_operations_tracker() -> SlowOperationsTracker:
    """Get global tracker."""
    return _tracker


__all__ = [
    "SlowOperation",
    "SlowOperationsTracker",
    "get_slow_operations_tracker",
]