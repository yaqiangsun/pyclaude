"""Bidirectional text reordering for terminal rendering."""
import os
from typing import List, Dict, Any, Optional


class ClusteredChar:
    """Represents a character with layout properties."""
    def __init__(
        self,
        value: str,
        width: int = 1,
        style_id: int = 0,
        hyperlink: Optional[str] = None,
    ):
        self.value = value
        self.width = width
        self.style_id = style_id
        self.hyperlink = hyperlink


def _needs_software_bidi() -> bool:
    """Check if terminal needs software bidi support."""
    # Windows
    if os.name == 'nt':
        return True
    # Windows Terminal / WSL
    if os.environ.get('WT_SESSION'):
        return True
    # VS Code integrated terminal
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        return True
    return False


_NEEDS_BIDI = _needs_software_bidi()


def reorder_bidi(chars: List[ClusteredChar]) -> List[ClusteredChar]:
    """Reorder array of ClusteredChars from logical to visual order.

    On macOS/Linux terminals, returns input unchanged (native bidi support).
    On Windows terminals, applies Unicode Bidi Algorithm.
    """
    if not _NEEDS_BIDI or not chars:
        return chars

    # TODO: Implement full bidi algorithm using python-bidi
    # For now, just return as-is
    return chars


def get_bidi_support() -> bool:
    """Check if software bidi is enabled."""
    return _NEEDS_BIDI


__all__ = ['ClusteredChar', 'reorder_bidi', 'get_bidi_support']