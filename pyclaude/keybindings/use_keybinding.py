"""Use keybinding hook."""
from __future__ import annotations
from typing import Any, Callable, Optional


def use_keybinding(
    key: str,
    action: Callable,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Register a keybinding with an action."""
    pass  # Placeholder - would integrate with input handler


__all__ = ['use_keybinding']