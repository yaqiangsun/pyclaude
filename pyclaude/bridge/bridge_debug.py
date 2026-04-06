"""Bridge debug utilities."""

import os
import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field


DEBUG_ENABLED = os.environ.get('CLAUDE_BRIDGE_DEBUG', '').lower() == 'true'


@dataclass
class DebugEntry:
    """A debug log entry."""
    timestamp: float
    message: str
    level: str = 'info'
    data: Dict[str, Any] = field(default_factory=dict)


class BridgeDebugger:
    """Debug logging for bridge."""

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self._entries: List[DebugEntry] = []

    def log(self, message: str, level: str = 'info', **data: Any) -> None:
        """Log a debug message."""
        if not DEBUG_ENABLED and level != 'error':
            return

        entry = DebugEntry(
            timestamp=time.time(),
            message=message,
            level=level,
            data=data,
        )
        self._entries.append(entry)

        if len(self._entries) > self.max_entries:
            self._entries.pop(0)

    def error(self, message: str, **data: Any) -> None:
        """Log an error."""
        self.log(message, level='error', **data)

    def warning(self, message: str, **data: Any) -> None:
        """Log a warning."""
        self.log(message, level='warning', **data)

    def get_entries(self, level: Optional[str] = None) -> List[DebugEntry]:
        """Get debug entries."""
        if level:
            return [e for e in self._entries if e.level == level]
        return list(self._entries)

    def clear(self) -> None:
        """Clear debug entries."""
        self._entries.clear()


# Global debugger
_bridge_debugger = BridgeDebugger()


def get_debugger() -> BridgeDebugger:
    """Get the global bridge debugger."""
    return _bridge_debugger


def bridge_debug(message: str, **data: Any) -> None:
    """Log a bridge debug message."""
    _bridge_debugger.log(message, **data)


__all__ = ['DEBUG_ENABLED', 'BridgeDebugger', 'get_debugger', 'bridge_debug']