"""
Analytics service for tracking events and metrics.
"""

from typing import Any, Dict, Optional, Callable
from datetime import datetime
import os


class AnalyticsEvent:
    """Represents an analytics event."""

    def __init__(self, name: str, properties: Optional[Dict[str, Any]] = None):
        self.name = name
        self.properties = properties or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "properties": self.properties,
            "timestamp": self.timestamp,
        }


class AnalyticsService:
    """Analytics service for tracking user events."""

    def __init__(self):
        self._events: list[AnalyticsEvent] = []
        self._enabled = os.environ.get("CLAUDE_CODE_ANALYTICS_ENABLED", "true").lower() == "true"

    def track_event(self, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Track an analytics event."""
        if not self._enabled:
            return
        event = AnalyticsEvent(name, properties)
        self._events.append(event)

    def get_events(self) -> list[AnalyticsEvent]:
        """Get all tracked events."""
        return self._events.copy()

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()


# Global analytics instance
_analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get the global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service


def log_event(name: str, properties: Optional[Dict[str, Any]] = None) -> None:
    """Log an analytics event."""
    get_analytics_service().track_event(name, properties)


__all__ = [
    "AnalyticsEvent",
    "AnalyticsService",
    "get_analytics_service",
    "log_event",
]