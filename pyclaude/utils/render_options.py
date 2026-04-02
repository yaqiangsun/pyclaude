"""
Render options utilities.

Rendering configuration.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class RenderMode(str, Enum):
    """Render modes."""
    PLAIN = "plain"
    MARKDOWN = "markdown"
    ANSI = "ansi"
    HTML = "html"


@dataclass
class RenderOptions:
    """Options for rendering."""
    mode: RenderMode = RenderMode.ANSI
    width: int = 80
    height: int = 24
    theme: str = "dark"
    syntax_highlight: bool = True
    show_progress: bool = True
    max_output_lines: Optional[int] = None


def get_default_render_options() -> RenderOptions:
    """Get default render options.

    Returns:
        Default options
    """
    return RenderOptions()


def parse_render_mode(mode: str) -> RenderMode:
    """Parse render mode string.

    Args:
        mode: Mode string

    Returns:
        Render mode
    """
    mode_lower = mode.lower()
    for m in RenderMode:
        if m.value == mode_lower:
            return m
    return RenderMode.ANSI


__all__ = [
    "RenderMode",
    "RenderOptions",
    "get_default_render_options",
    "parse_render_mode",
]