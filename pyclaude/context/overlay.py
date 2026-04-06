"""Overlay context for modal/dialog overlays."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OverlayType(str, Enum):
    """Types of overlays."""
    MODAL = 'modal'
    DIALOG = 'dialog'
    TOAST = 'toast'
    POPOVER = 'popover'


@dataclass
class Overlay:
    """An overlay."""
    id: str
    type: OverlayType
    title: str = ''
    content: str = ''
    metadata: Dict[str, Any] = field(default_factory=dict)


class OverlayContext:
    """Context for managing overlays."""

    def __init__(self):
        self._overlays: List[Overlay] = []

    def show_overlay(self, overlay: Overlay) -> None:
        """Show an overlay."""
        self._overlays.append(overlay)

    def hide_overlay(self, overlay_id: str) -> None:
        """Hide an overlay."""
        self._overlays = [o for o in self._overlays if o.id != overlay_id]

    def get_overlays(self) -> List[Overlay]:
        """Get all overlays."""
        return list(self._overlays)

    def clear(self) -> None:
        """Clear all overlays."""
        self._overlays.clear()


# Global context
_overlay_context = OverlayContext()


def get_overlay_context() -> OverlayContext:
    """Get the global overlay context."""
    return _overlay_context


__all__ = ['OverlayType', 'Overlay', 'OverlayContext', 'get_overlay_context']