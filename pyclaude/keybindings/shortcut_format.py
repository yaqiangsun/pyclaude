"""Format shortcut display."""
from __future__ import annotations
from typing import Optional


def format_shortcut(key: str, modifiers: Optional[list[str]] = None) -> str:
    """Format a shortcut for display."""
    parts = modifiers or []
    parts.append(key)
    return '+'.join(parts)


__all__ = ['format_shortcut']