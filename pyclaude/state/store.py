"""State store."""

from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


Listener = Callable[[Dict[str, Any]], None]


@dataclass
class Store:
    """Simple state store."""
    _state: Dict[str, Any] = field(default_factory=dict)
    _listeners: List[Listener] = field(default_factory=list)
    _history: List[Dict[str, Any]] = field(default_factory=list)
    _history_index: int = -1

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        return self._state.copy()

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set state."""
        self._state = state.copy()
        self._notify()

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update state with partial changes."""
        self._state.update(updates)
        self._notify()

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """Subscribe to state changes."""
        self._listeners.append(listener)

        def unsubscribe():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    def _notify(self) -> None:
        """Notify all listeners."""
        for listener in self._listeners:
            listener(self._state)

    # History management
    def push_state(self, state: Dict[str, Any]) -> None:
        """Push state to history."""
        # Remove any forward history
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]

        self._history.append(state.copy())
        self._history_index = len(self._history) - 1

    def undo(self) -> Optional[Dict[str, Any]]:
        """Undo to previous state."""
        if self._history_index > 0:
            self._history_index -= 1
            self._state = self._history[self._history_index].copy()
            self._notify()
            return self._state
        return None

    def redo(self) -> Optional[Dict[str, Any]]:
        """Redo to next state."""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._state = self._history[self._history_index].copy()
            self._notify()
            return self._state
        return None


# Global store
_store: Optional[Store] = None


def get_store() -> Store:
    """Get the global store."""
    global _store
    if _store is None:
        _store = Store()
    return _store


__all__ = ['Store', 'Listener', 'get_store']