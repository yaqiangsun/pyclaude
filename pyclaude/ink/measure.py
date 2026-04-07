"""
Ink measure - Measure text and element dimensions.
"""
from typing import Optional, Tuple
from .string_width import string_width


class MeasureResult:
    """Result of measuring text."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height


def measure_text(
    text: str,
    col_width: int = 80,
) -> MeasureResult:
    """
    Measure text dimensions.

    Args:
        text: Text to measure
        col_width: Column width for wrapping

    Returns:
        MeasureResult with width and height
    """
    if not text:
        return MeasureResult(0, 0)

    lines = text.split('\n')
    max_width = 0
    total_height = len(lines)

    for line in lines:
        width = string_width(line)
        max_width = max(max_width, width)

    return MeasureResult(max_width, total_height)


def measure_element(
    text: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Tuple[int, int]:
    """
    Measure an element's dimensions.

    Args:
        text: Element text content
        width: Constrained width (None = auto)
        height: Constrained height (None = auto)

    Returns:
        Tuple of (width, height)
    """
    result = measure_text(text, width or 80)

    return (
        width if width else result.width,
        height if height else result.height,
    )


def wrap_text(
    text: str,
    width: int,
) -> list:
    """
    Wrap text to fit within width.

    Args:
        text: Text to wrap
        width: Maximum width per line

    Returns:
        List of wrapped lines
    """
    if not text:
        return []

    lines = text.split('\n')
    wrapped = []

    for line in lines:
        if string_width(line) <= width:
            wrapped.append(line)
            continue

        # Split line
        words = line.split()
        current_line = ""
        current_width = 0

        for word in words:
            word_width = string_width(word)
            space_width = 1 if current_line else 0

            if current_width + space_width + word_width <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
                current_width += space_width + word_width
            else:
                if current_line:
                    wrapped.append(current_line)
                current_line = word
                current_width = word_width

        if current_line:
            wrapped.append(current_line)

    return wrapped


__all__ = ['MeasureResult', 'measure_text', 'measure_element', 'wrap_text']