"""Keybinding schema."""
from __future__ import annotations
from typing import Any, Optional, TypedDict


class KeybindingSchema(TypedDict):
    """Schema for keybinding configuration."""

    key: str
    action: str
    description: str
    context: Optional[str]


__all__ = ['KeybindingSchema']