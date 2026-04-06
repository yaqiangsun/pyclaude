"""Diagnostic tracking service."""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiagnosticEvent:
    """A diagnostic event."""
    timestamp: datetime
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)


class DiagnosticTracker:
    """Track diagnostic events."""

    def __init__(self):
        self._events: List[DiagnosticEvent] = []

    def track(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Track a diagnostic event."""
        event = DiagnosticEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            data=data or {},
        )
        self._events.append(event)

    def get_events(self, event_type: str = None) -> List[DiagnosticEvent]:
        """Get diagnostic events."""
        if event_type:
            return [e for e in self._events if e.event_type == event_type]
        return list(self._events)

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()


# Global tracker
_diagnostic_tracker = DiagnosticTracker()


def get_diagnostic_tracker() -> DiagnosticTracker:
    """Get the global diagnostic tracker."""
    return _diagnostic_tracker


__all__ = ['DiagnosticEvent', 'DiagnosticTracker', 'get_diagnostic_tracker']