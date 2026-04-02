"""
Slice ANSI utilities.

Handle ANSI escape sequences in text slicing.
"""

import re


# ANSI escape sequence pattern
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def slice_ansi(text: str, start: int, end: int) -> str:
    """Slice text while accounting for ANSI codes.

    Args:
        text: Text with possible ANSI codes
        start: Start index (in visible characters)
        end: End index (in visible characters)

    Returns:
        Sliced text
    """
    # Strip ANSI codes first to find visible length
    visible_text = ANSI_ESCAPE.sub('', text)
    visible_len = len(visible_text)

    # Clamp indices
    start = max(0, min(start, visible_len))
    end = max(0, min(end, visible_len))

    if start >= end:
        return ''

    # Find positions in original text
    result = []
    pos = 0
    visible_pos = 0
    i = 0
    n = len(text)

    while i < n and visible_pos < end:
        if text[i] == '\x1b' and i + 1 < n and text[i + 1] == '[':
            # Copy ANSI sequence
            j = i + 2
            while j < n and text[j] not in 'ABCDEFGHIJKLMNOQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
                j += 1
            if visible_pos >= start:
                result.append(text[i:j + 1])
            i = j + 1
        else:
            if visible_pos >= start:
                result.append(text[i])
            visible_pos += 1
            i += 1

    return ''.join(result)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences.

    Args:
        text: Text with ANSI codes

    Returns:
        Plain text
    """
    return ANSI_ESCAPE.sub('', text)


def ansi_length(text: str) -> int:
    """Get visible length of text with ANSI codes.

    Args:
        text: Text with possible ANSI codes

    Returns:
        Visible character count
    """
    return len(strip_ansi(text))


__all__ = [
    "slice_ansi",
    "strip_ansi",
    "ansi_length",
    "ANSI_ESCAPE",
]