"""
Profiler base utilities.

Base profiling infrastructure.
"""

import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class ProfileEntry:
    """Profile entry."""
    name: str
    duration_ms: float
    start_time: float
    end_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class Profiler:
    """Simple profiler."""

    def __init__(self):
        self.entries: list = []
        self._current: Optional[ProfileEntry] = None

    def start(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Start profiling.

        Args:
            name: Profile name
            metadata: Optional metadata
        """
        self._current = ProfileEntry(
            name=name,
            duration_ms=0,
            start_time=time.time(),
            end_time=0,
            metadata=metadata or {},
        )

    def stop(self) -> Optional[ProfileEntry]:
        """Stop profiling.

        Returns:
            Profile entry
        """
        if self._current:
            self._current.end_time = time.time()
            self._current.duration_ms = (self._current.end_time - self._current.start_time) * 1000
            self.entries.append(self._current)
            result = self._current
            self._current = None
            return result
        return None

    def profile(self, fn: Callable) -> Callable:
        """Decorator to profile function.

        Args:
            fn: Function to profile

        Returns:
            Wrapped function
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            self.start(fn.__name__)
            try:
                return fn(*args, **kwargs)
            finally:
                self.stop()
        return wrapper


# Global profiler
_profiler = Profiler()


def get_profiler() -> Profiler:
    """Get global profiler."""
    return _profiler


__all__ = [
    "ProfileEntry",
    "Profiler",
    "get_profiler",
]