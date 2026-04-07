"""Match keybinding."""
from __future__ import annotations
from typing import Any, Optional


def match_keybinding(key: str, bindings: dict[str, Any]) -> Optional[dict]:
    """Match a keypress against bindings."""
    key_lower = key.lower()
    return bindings.get(key_lower)


__all__ = ['match_keybinding']