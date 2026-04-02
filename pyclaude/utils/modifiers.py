"""
Modifiers utilities.

Keyboard modifier handling.
"""

import os
from typing import Set


# Modifier states
class Modifiers:
    """Keyboard modifier states."""

    def __init__(self):
        self.shift = False
        self.ctrl = False
        self.alt = False
        self.meta = False

    def to_set(self) -> Set[str]:
        """Convert to set of active modifiers.

        Returns:
            Set of modifier names
        """
        result = set()
        if self.shift:
            result.add("shift")
        if self.ctrl:
            result.add("ctrl")
        if self.alt:
            result.add("alt")
        if self.meta:
            result.add("meta")
        return result

    def __repr__(self) -> str:
        return f"Modifiers({self.to_set()})"


def parse_modifier_key(key: str) -> tuple[Modifiers, str]:
    """Parse modifier key combination.

    Args:
        key: Key string like "Ctrl+C"

    Returns:
        (Modifiers, base_key)
    """
    mods = Modifiers()
    parts = key.split("+")

    for part in parts[:-1]:
        part = part.strip().lower()
        if part == "ctrl" or part == "control":
            mods.ctrl = True
        elif part == "shift":
            mods.shift = True
        elif part == "alt":
            mods.alt = True
        elif part == "meta" or part == "cmd":
            mods.meta = True

    base_key = parts[-1].strip() if parts else ""
    return mods, base_key


__all__ = [
    "Modifiers",
    "parse_modifier_key",
]