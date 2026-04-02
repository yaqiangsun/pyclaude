"""
String utilities.

String manipulation helpers.
"""

import re
from typing import Optional, List


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def word_wrap(text: str, width: int) -> List[str]:
    """Wrap text to specified width.

    Args:
        text: Text to wrap
        width: Line width

    Returns:
        List of wrapped lines
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if len(test_line) <= width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences.

    Args:
        text: Text with ANSI codes

    Returns:
        Plain text
    """
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case.

    Args:
        text: camelCase string

    Returns:
        snake_case string
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        text: snake_case string

    Returns:
        camelCase string
    """
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def escape_regex(text: str) -> str:
    """Escape regex special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return re.escape(text)


__all__ = [
    "truncate",
    "word_wrap",
    "strip_ansi",
    "camel_to_snake",
    "snake_to_camel",
    "escape_regex",
]