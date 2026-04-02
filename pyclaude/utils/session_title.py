"""
Session title utilities.

Session title generation and management.
"""

import os
from typing import Optional


def generate_session_title(cwd: str, first_message: Optional[str] = None) -> str:
    """Generate session title.

    Args:
        cwd: Current working directory
        first_message: First user message

    Returns:
        Session title
    """
    # Use directory name as base
    title = os.path.basename(cwd) or "Claude"

    if first_message:
        # Extract first few words from message
        words = first_message.split()[:3]
        if words:
            title += f" - {' '.join(words)}"

    return title


def truncate_title(title: str, max_length: int = 50) -> str:
    """Truncate session title.

    Args:
        title: Title to truncate
        max_length: Maximum length

    Returns:
        Truncated title
    """
    if len(title) <= max_length:
        return title
    return title[:max_length - 3] + "..."


__all__ = [
    "generate_session_title",
    "truncate_title",
]