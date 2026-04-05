"""Find the widest line in a multiline string."""
from .string_width import string_width


def widest_line(text: str) -> int:
    """Find the maximum width of any line in a multiline string.

    Args:
        text: Multiline text string

    Returns:
        Width of the widest line in cells
    """
    if not text:
        return 0

    max_width = 0
    start = 0

    while start <= len(text):
        end = text.find('\n', start)
        if end == -1:
            line = text[start:]
        else:
            line = text[start:end]

        max_width = max(max_width, string_width(line))

        if end == -1:
            break
        start = end + 1

    return max_width


__all__ = ['widest_line']