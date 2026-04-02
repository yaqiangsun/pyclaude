"""
Use copy on select hook.

Auto-copy the selection to the clipboard when the user finishes dragging
or multi-clicks to select a word/line.
"""

from typing import Optional, Callable

# Global state for copy on select
_copied_ref = False


def use_copy_on_select(
    selection: Any,
    is_active: bool,
    on_copied: Optional[Callable[[str], None]] = None,
) -> None:
    """Auto-copy selection to clipboard.

    Args:
        selection: Selection object with subscribe, get_state, has_selection, copy_selection_no_clear methods
        is_active: Whether copy on select is active
        on_copied: Optional callback when text is copied
    """
    global _copied_ref

    if not is_active:
        return

    # Placeholder implementation - actual would subscribe to selection changes
    pass


class SelectionState:
    """Represents selection state."""

    def __init__(self):
        self.is_dragging = False
        self.start = None
        self.end = None

    def has_selection(self) -> bool:
        """Check if there's a selection."""
        return self.start is not None and self.end is not None

    def copy_selection_no_clear(self) -> str:
        """Copy selection without clearing."""
        return ""


class SelectionManager:
    """Manages selection state."""

    def __init__(self):
        self._state = SelectionState()
        self._subscribers = []

    def subscribe(self, callback: Callable) -> Callable:
        """Subscribe to selection changes."""
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)

    def get_state(self) -> SelectionState:
        """Get current selection state."""
        return self._state

    def has_selection(self) -> bool:
        """Check if there's a selection."""
        return self._state.has_selection()

    def copy_selection_no_clear(self) -> str:
        """Copy selection without clearing."""
        return ""

    def set_selection_bg_color(self, color: str) -> None:
        """Set selection background color."""
        pass


__all__ = ["SelectionState", "SelectionManager", "use_copy_on_select"]