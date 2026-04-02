"""
Words utilities.

Word processing helpers.
"""

import re
from typing import List, Optional


def split_words(text: str) -> List[str]:
    """Split text into words.

    Args:
        text: Text to split

    Returns:
        List of words
    """
    return re.findall(r'\b\w+\b', text)


def count_words(text: str) -> int:
    """Count words in text.

    Args:
        text: Text to count

    Returns:
        Word count
    """
    return len(split_words(text))


def capitalize_words(text: str) -> str:
    """Capitalize first letter of each word.

    Args:
        text: Text to capitalize

    Returns:
        Capitalized text
    """
    return " ".join(word.capitalize() for word in text.split())


def pluralize(word: str, count: int) -> str:
    """Pluralize word based on count.

    Args:
        word: Word to pluralize
        count: Count

    Returns:
        Singular or plural form
    """
    if count == 1:
        return word

    # Simple pluralization rules
    if word.endswith('y'):
        return word[:-1] + 'ies'
    if word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    return word + 's'


__all__ = [
    "split_words",
    "count_words",
    "capitalize_words",
    "pluralize",
]