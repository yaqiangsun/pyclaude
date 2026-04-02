"""
Debug filter utilities.

Parse debug filter string into a filter configuration and check if
debug messages should be shown based on categories.
"""

import re
from functools import lru_cache
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class DebugFilter:
    """Debug filter configuration."""
    include: List[str]
    exclude: List[str]
    is_exclusive: bool


@lru_cache(maxsize=1)
def parse_debug_filter(filter_string: Optional[str]) -> Optional[DebugFilter]:
    """Parse debug filter string into a filter configuration.

    Examples:
    - "api,hooks" -> include only api and hooks categories
    - "!1p,!file" -> exclude logging and file categories
    - undefined/empty -> no filtering (show all)

    Args:
        filter_string: The filter string to parse

    Returns:
        DebugFilter configuration or None if no filter
    """
    if not filter_string or filter_string.strip() == "":
        return None

    filters = [f.strip() for f in filter_string.split(",") if f.strip()]

    if not filters:
        return None

    # Check for mixed inclusive/exclusive filters
    has_exclusive = any(f.startswith("!") for f in filters)
    has_inclusive = any(not f.startswith("!") for f in filters)

    if has_exclusive and has_inclusive:
        # Mixed filters - show all messages
        return None

    # Clean up filters (remove ! prefix) and normalize
    clean_filters = [f.lstrip("!").lower() for f in filters]

    return DebugFilter(
        include=[] if has_exclusive else clean_filters,
        exclude=clean_filters if has_exclusive else [],
        is_exclusive=has_exclusive,
    )


def extract_debug_categories(message: str) -> List[str]:
    """Extract debug categories from a message.

    Supports multiple patterns:
    - "category: message" -> ["category"]
    - "[CATEGORY] message" -> ["category"]
    - "MCP server \"name\": message" -> ["mcp", "name"]
    - "[ANT-ONLY] 1P event: tengu_timer" -> ["ant-only", "1p"]

    Returns:
        Lowercase categories for case-insensitive matching
    """
    categories = []

    # Pattern: MCP server "servername"
    mcp_match = re.match(r'^MCP server ["\']([^"\']+)["\']', message)
    if mcp_match and mcp_match.group(1):
        categories.append("mcp")
        categories.append(mcp_match.group(1).lower())
    else:
        # Pattern: "category: message"
        prefix_match = re.match(r"^([^:[]+):", message)
        if prefix_match and prefix_match.group(1):
            categories.append(prefix_match.group(1).strip().lower())

    # Pattern: [CATEGORY] at the start
    bracket_match = re.match(r"^\[([^\]]+)]", message)
    if bracket_match and bracket_match.group(1):
        categories.append(bracket_match.group(1).strip().lower())

    # Pattern: 1P event
    if "1p event:" in message.lower():
        categories.append("1p")

    # Pattern: secondary categories
    secondary_match = re.search(r":\s*([^:]+?)(?:\s+(?:type|mode|status|event))?:", message)
    if secondary_match and secondary_match.group(1):
        secondary = secondary_match.group(1).strip().lower()
        if len(secondary) < 30 and " " not in secondary:
            categories.append(secondary)

    return list(dict.fromkeys(categories))  # Remove duplicates while preserving order


def should_show_debug_categories(
    categories: List[str],
    filter_config: Optional[DebugFilter],
) -> bool:
    """Check if debug message should be shown based on filter.

    Args:
        categories: Categories extracted from the message
        filter_config: Parsed filter configuration

    Returns:
        True if message should be shown
    """
    if not filter_config:
        return True

    if not categories:
        return False

    if filter_config.is_exclusive:
        return not any(cat in filter_config.exclude for cat in categories)
    else:
        return any(cat in filter_config.include for cat in categories)


def should_show_debug_message(
    message: str,
    filter_config: Optional[DebugFilter],
) -> bool:
    """Check if a debug message should be shown.

    Args:
        message: The debug message
        filter_config: Parsed filter configuration

    Returns:
        True if message should be shown
    """
    if not filter_config:
        return True

    categories = extract_debug_categories(message)
    return should_show_debug_categories(categories, filter_config)


__all__ = [
    "DebugFilter",
    "parse_debug_filter",
    "extract_debug_categories",
    "should_show_debug_categories",
    "should_show_debug_message",
]