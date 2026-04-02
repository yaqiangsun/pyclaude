"""
Horizontal scroll utilities.

Handle horizontal scrolling.
"""

from typing import List


def wrap_lines(lines: List[str], width: int) -> List[str]:
    """Wrap lines to specified width.

    Args:
        lines: Input lines
        width: Max width

    Returns:
        Wrapped lines
    """
    result = []
    for line in lines:
        while len(line) > width:
            result.append(line[:width])
            line = line[width:]
        result.append(line)
    return result


__all__ = ["wrap_lines"]