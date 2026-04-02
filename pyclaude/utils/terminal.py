"""
Terminal utilities.

Terminal detection and configuration.
"""

import os
import sys
import shutil
from typing import Optional, Tuple, Dict, Any


def get_terminal_size() -> Tuple[int, int]:
    """Get terminal size.

    Returns:
        (columns, rows)
    """
    try:
        size = shutil.get_terminal_size()
        return (size.columns, size.lines)
    except Exception:
        return (80, 24)


def get_terminal_type() -> Optional[str]:
    """Get terminal type.

    Returns:
        Terminal type string
    """
    return os.environ.get("TERM")


def is_terminal() -> bool:
    """Check if stdout is a terminal.

    Returns:
        True if terminal
    """
    return sys.stdout.isatty()


def get_terminal_colors() -> int:
    """Get number of terminal colors.

    Returns:
        Color count
    """
    term = os.environ.get("TERM", "")
    if "256" in term:
        return 256
    if "color" in term:
        return 16
    return 8


__all__ = [
    "get_terminal_size",
    "get_terminal_type",
    "is_terminal",
    "get_terminal_colors",
]