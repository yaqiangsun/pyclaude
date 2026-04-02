"""
Semver utilities.

Semantic version comparison.
"""

import re
from typing import Optional, Tuple


def parse_version(version: str) -> Optional[Tuple[int, int, int]]:
    """Parse semantic version.

    Args:
        version: Version string (e.g., "1.2.3")

    Returns:
        (major, minor, patch) tuple
    """
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None


def compare_versions(v1: str, v2: str) -> int:
    """Compare two semantic versions.

    Args:
        v1: First version
        v2: Second version

    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    p1 = parse_version(v1)
    p2 = parse_version(v2)

    if not p1 or not p2:
        return 0

    if p1 < p2:
        return -1
    elif p1 > p2:
        return 1
    return 0


def gt(v1: str, v2: str) -> bool:
    """Check if v1 > v2."""
    return compare_versions(v1, v2) > 0


def gte(v1: str, v2: str) -> bool:
    """Check if v1 >= v2."""
    return compare_versions(v1, v2) >= 0


def lt(v1: str, v2: str) -> bool:
    """Check if v1 < v2."""
    return compare_versions(v1, v2) < 0


def lte(v1: str, v2: str) -> bool:
    """Check if v1 <= v2."""
    return compare_versions(v1, v2) <= 0


def eq(v1: str, v2: str) -> bool:
    """Check if v1 == v2."""
    return compare_versions(v1, v2) == 0


__all__ = [
    "parse_version",
    "compare_versions",
    "gt",
    "gte",
    "lt",
    "lte",
    "eq",
]