"""
Terminal panel utilities.

Terminal panel/region management.
"""

from typing import Optional, Tuple


def create_panel(
    content: str,
    title: Optional[str] = None,
    width: Optional[int] = None,
) -> str:
    """Create a terminal panel.

    Args:
        content: Panel content
        title: Panel title
        width: Panel width

    Returns:
        Panel string
    """
    lines = content.split("\n")
    max_len = max(len(line) for line in lines) if lines else 0

    if width:
        max_len = max(max_len, width)

    result = []

    # Top border
    if title:
        title_len = len(title)
        side_len = (max_len - title_len - 2) // 2
        result.append("┌" + "─" * side_len + " " + title + " " + "─" * (max_len - side_len - title_len - 2) + "┐")
    else:
        result.append("┌" + "─" * max_len + "┐")

    # Content
    for line in lines:
        padding = max_len - len(line)
        result.append("│" + line + " " * padding + "│")

    # Bottom border
    result.append("└" + "─" * max_len + "┘")

    return "\n".join(result)


def close_panel() -> str:
    """Close panel marker.

    Returns:
        Close string
    """
    return "└" + "─" * 20 + "┘"


__all__ = [
    "create_panel",
    "close_panel",
]