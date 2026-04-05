"""App component - main application wrapper."""
from typing import Any, Dict, Optional


class App:
    """Main application component.

    This is a Python representation of the React App component.
    In the Python version, this serves as the entry point for the TUI.
    """

    def __init__(
        self,
        initial_state: Optional[Dict[str, Any]] = None,
        get_fps_metrics: Optional[callable] = None,
        stats: Optional[Dict[str, Any]] = None,
    ):
        self.initial_state = initial_state or {}
        self.get_fps_metrics = get_fps_metrics
        self.stats = stats
        self._state = initial_state or {}

    def set_state(self, new_state: Dict[str, Any]) -> None:
        """Update application state."""
        self._state.update(new_state)

    def get_state(self) -> Dict[str, Any]:
        """Get current application state."""
        return self._state.copy()

    def render(self) -> str:
        """Render the application."""
        return "PyClaude App"


__all__ = ['App']