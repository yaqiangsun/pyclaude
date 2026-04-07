"""
Ink keypress parsing - Parse keyboard input.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class KeyType(Enum):
    """Key type."""
    CHAR = "char"
    ESCAPE = "escape"
    FUNCTION = "function"
    ARROW = "arrow"
    SPECIAL = "special"


class KeyModifiers(Enum):
    """Key modifiers."""
    NONE = 0
    SHIFT = 1
    CTRL = 2
    ALT = 4
    META = 8


@dataclass
class Keypress:
    """Parsed keypress."""
    key: str
    type: KeyType
    alt: bool = False
    ctrl: bool = False
    shift: bool = False
    meta: bool = False

    def __str__(self) -> str:
        parts = []
        if self.ctrl:
            parts.append('ctrl')
        if self.alt:
            parts.append('alt')
        if self.meta:
            parts.append('meta')
        if self.shift:
            parts.append('shift')
        parts.append(self.key)
        return '+'.join(parts)


# Escape sequence mappings
ESCAPE_SEQUENCES = {
    '\x1b[A': ('up', KeyType.ARROW),
    '\x1b[B': ('down', KeyType.ARROW),
    '\x1b[C': ('right', KeyType.ARROW),
    '\x1b[D': ('left', KeyType.ARROW),
    '\x1b[H': ('home', KeyType.SPECIAL),
    '\x1b[F': ('end', KeyType.SPECIAL),
    '\x1b[P': ('delete', KeyType.SPECIAL),
    '\x1b[Q': ('insert', KeyType.SPECIAL),
    '\x1b[15~': ('f5', KeyType.FUNCTION),
    '\x1b[17~': ('f6', KeyType.FUNCTION),
    '\x1b[18~': ('f7', KeyType.FUNCTION),
    '\x1b[19~': ('f8', KeyType.FUNCTION),
    '\x1b[20~': ('f9', KeyType.FUNCTION),
    '\x1b[21~': ('f10', KeyType.FUNCTION),
    '\x1b[23~': ('f11', KeyType.FUNCTION),
    '\x1b[24~': ('f12', KeyType.FUNCTION),
}

# Extended escape sequences with modifiers
EXTENDED_SEQUENCES = {
    '\x1b[1;2A': ('up', KeyType.ARROW, True, False, False, False),   # shift+up
    '\x1b[1;2B': ('down', KeyType.ARROW, True, False, False, False),
    '\x1b[1;2C': ('right', KeyType.ARROW, True, False, False, False),
    '\x1b[1;2D': ('left', KeyType.ARROW, True, False, False, False),
    '\x1b[1;5A': ('up', KeyType.ARROW, False, True, False, False),   # ctrl+up
    '\x1b[1;5B': ('down', KeyType.ARROW, False, True, False, False),
    '\x1b[1;5C': ('right', KeyType.ARROW, False, True, False, False),
    '\x1b[1;5D': ('left', KeyType.ARROW, False, True, False, False),
}


def parse_keypress(data: str) -> Optional[Keypress]:
    """
    Parse keyboard input data into a Keypress.

    Args:
        data: Raw input data from terminal

    Returns:
        Parsed Keypress or None
    """
    if not data:
        return None

    # Handle escape sequences first
    if data.startswith('\x1b'):
        return _parse_escape_sequence(data)

    # Handle regular characters
    if len(data) == 1:
        char = data
        return Keypress(
            key=char,
            type=KeyType.CHAR,
            ctrl=ord(char) < 32,
        )

    return None


def _parse_escape_sequence(data: str) -> Optional[Keypress]:
    """Parse an escape sequence."""
    # Simple escape (just escape key)
    if data == '\x1b':
        return Keypress(key='escape', type=KeyType.ESCAPE)

    # Check extended sequences first
    for seq, params in EXTENDED_SEQUENCES.items():
        if data.startswith(seq):
            if len(params) == 2:
                key, key_type = params
                return Keypress(key=key, type=key_type)
            else:
                key, key_type, shift, ctrl, alt, meta = params
                return Keypress(
                    key=key, type=key_type,
                    shift=shift, ctrl=ctrl, alt=alt, meta=meta,
                )

    # Check standard sequences
    for seq, params in ESCAPE_SEQUENCES.items():
        if data.startswith(seq):
            if len(params) == 2:
                key, key_type = params
                return Keypress(key=key, type=key_type)

    # Unknown escape sequence
    return Keypress(key='unknown', type=KeyType.ESCAPE)


def is_printable(keypress: Keypress) -> bool:
    """Check if a keypress produces printable output."""
    return (
        keypress.type == KeyType.CHAR and
        not keypress.ctrl and
        not keypress.alt
    )


__all__ = [
    'KeyType',
    'KeyModifiers',
    'Keypress',
    'parse_keypress',
    'is_printable',
]