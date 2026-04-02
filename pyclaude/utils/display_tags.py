"""
Display tags utility.

Strips XML-like tags from display titles.
"""

import re

# Matches any XML-like <tag>...</tag> block (lowercase tag names, optional
# attributes, multi-line content)
XML_TAG_BLOCK_PATTERN = re.compile(
    r"<([a-z][\w-]*)(?:\s[^>]*)?>[\s\S]*?</\1>\n?",
    re.IGNORECASE,
)

# Strip only IDE-injected context tags (ide_opened_file, ide_selection)
IDE_CONTEXT_TAGS_PATTERN = re.compile(
    r"<(ide_opened_file|ide_selection)(?:\s[^>]*)?>[\s\S]*?</\1>\n?",
    re.IGNORECASE,
)


def strip_display_tags(text: str) -> str:
    """Strip XML-like tag blocks from text for use in UI titles.

    If stripping would result in empty text, returns the original unchanged.

    Args:
        text: The text to strip tags from

    Returns:
        Text with XML-like tags removed, or original if result would be empty
    """
    result = XML_TAG_BLOCK_PATTERN.sub("", text).strip()
    return result or text


def strip_display_tags_allow_empty(text: str) -> str:
    """Like strip_display_tags but returns empty string when all content is tags.

    Args:
        text: The text to strip tags from

    Returns:
        Text with XML-like tags removed
    """
    return XML_TAG_BLOCK_PATTERN.sub("", text).strip()


def strip_ide_context_tags(text: str) -> str:
    """Strip only IDE-injected context tags (ide_opened_file, ide_selection).

    Args:
        text: The text to strip IDE context tags from

    Returns:
        Text with IDE context tags removed
    """
    return IDE_CONTEXT_TAGS_PATTERN.sub("", text).strip()


__all__ = [
    "strip_display_tags",
    "strip_display_tags_allow_empty",
    "strip_ide_context_tags",
]