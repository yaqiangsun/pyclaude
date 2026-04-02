"""
Release notes utilities.

Release notes management.
"""

import os
from typing import Optional, List


def get_release_notes_path() -> str:
    """Get release notes file path.

    Returns:
        Release notes path
    """
    config_dir = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    return os.path.join(config_dir, "cache", "changelog.md")


def has_seen_release_notes(version: str) -> bool:
    """Check if release notes for version were seen.

    Args:
        version: Version string

    Returns:
        True if seen
    """
    return False


def mark_release_notes_seen(version: str) -> None:
    """Mark release notes as seen.

    Args:
        version: Version string
    """
    pass


__all__ = [
    "get_release_notes_path",
    "has_seen_release_notes",
    "mark_release_notes_seen",
]