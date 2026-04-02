"""
Cursor utilities.

Terminal cursor movement and manipulation functions.
"""

import sys


def cursor_up(n: int = 1) -> str:
    """Move cursor up n lines."""
    return f"\x1b[{n}A"


def cursor_down(n: int = 1) -> str:
    """Move cursor down n lines."""
    return f"\x1b[{n}B"


def cursor_forward(n: int = 1) -> str:
    """Move cursor forward n columns."""
    return f"\x1b[{n}C"


def cursor_back(n: int = 1) -> str:
    """Move cursor back n columns."""
    return f"\x1b[{n}D"


def cursor_next_line(n: int = 1) -> str:
    """Move cursor to beginning of line n lines down."""
    return f"\x1b[{n}E"


def cursor_previous_line(n: int = 1) -> str:
    """Move cursor to beginning of line n lines up."""
    return f"\x1b[{n}F"


def cursor_column(col: int) -> str:
    """Move cursor to column."""
    return f"\x1b[{col}G"


def cursor_position(row: int, col: int) -> str:
    """Move cursor to position (row, col)."""
    return f"\x1b[{row};{col}H"


def erase_display(mode: int = 0) -> str:
    """Erase display.

    Args:
        mode: 0=from cursor to end, 1=from start to cursor, 2=entire screen
    """
    return f"\x1b[{mode}J"


def erase_line(mode: int = 0) -> str:
    """Erase line.

    Args:
        mode: 0=from cursor to end, 1=from start to cursor, 2=entire line
    """
    return f"\x1b[{mode}K"


def scroll_up(n: int = 1) -> str:
    """Scroll screen up n lines."""
    return f"\x1b[{n}S"


def scroll_down(n: int = 1) -> str:
    """Scroll screen down n lines."""
    return f"\x1b[{n}T"


def save_cursor() -> str:
    """Save cursor position."""
    return "\x1b7"


def restore_cursor() -> str:
    """Restore cursor position."""
    return "\x1b8"


def hide_cursor() -> str:
    """Hide cursor."""
    return "\x1b[?25l"


def show_cursor() -> str:
    """Show cursor."""
    return "\x1b[?25h"


def cursor_is_supported() -> bool:
    """Check if terminal supports cursor control sequences."""
    return sys.stdout.isatty()


__all__ = [
    "cursor_up",
    "cursor_down",
    "cursor_forward",
    "cursor_back",
    "cursor_next_line",
    "cursor_previous_line",
    "cursor_column",
    "cursor_position",
    "erase_display",
    "erase_line",
    "scroll_up",
    "scroll_down",
    "save_cursor",
    "restore_cursor",
    "hide_cursor",
    "show_cursor",
    "cursor_is_supported",
]