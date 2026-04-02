"""
Semantic boolean utilities.

Boolean parsing with semantic meaning.
"""

from typing import Optional


def parse_boolean(value: any) -> Optional[bool]:
    """Parse value to boolean.

    Args:
        value: Value to parse

    Returns:
        Boolean or None if cannot parse
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower = value.lower()
        if lower in ("true", "1", "yes", "on", "enabled"):
            return True
        if lower in ("false", "0", "no", "off", "disabled"):
            return False

    if isinstance(value, int):
        return bool(value)

    return None


def is_truthy(value: any) -> bool:
    """Check if value is truthy.

    Args:
        value: Value to check

    Returns:
        True if truthy
    """
    result = parse_boolean(value)
    if result is not None:
        return result
    return bool(value)


def is_falsy(value: any) -> bool:
    """Check if value is falsy.

    Args:
        value: Value to check

    Returns:
        True if falsy
    """
    return not is_truthy(value)


__all__ = [
    "parse_boolean",
    "is_truthy",
    "is_falsy",
]