"""
Hyperlink utilities.

Terminal hyperlink handling.
"""

import os
from typing import Optional


def create_hyperlink(url: str, text: str) -> str:
    """Create terminal hyperlink.

    Args:
        url: Link URL
        text: Link text

    Returns:
        Hyperlink string
    """
    # OSC 8 hyperlinks for terminal support
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"


def is_hyperlink_supported() -> bool:
    """Check if terminal supports hyperlinks.

    Returns:
        True if supported
    """
    term = os.environ.get("TERM", "")
    # Most modern terminals support OSC 8
    unsupported = ["vt100", "ansi"]
    return not any(t in term.lower() for t in unsupported)


def parse_hyperlink(text: str) -> Optional[str]:
    """Extract URL from hyperlink.

    Args:
        text: Text containing hyperlink

    Returns:
        URL or None
    """
    # Simple extraction - looks for OSC 8 sequences
    import re
    match = re.search(r'\x1b\]8;;(.+?)\\', text)
    if match:
        return match.group(1)
    return None


__all__ = [
    "create_hyperlink",
    "is_hyperlink_supported",
    "parse_hyperlink",
]