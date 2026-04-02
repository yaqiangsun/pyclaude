"""
Screenshot utilities.

Screenshot capture and clipboard handling.
"""

import os
from typing import Optional
import base64


def capture_screenshot() -> Optional[bytes]:
    """Capture screenshot.

    Returns:
        Screenshot data or None
    """
    # Platform-specific implementation would go here
    return None


def save_screenshot(data: bytes, path: str) -> bool:
    """Save screenshot to file.

    Args:
        data: Screenshot data
        path: Output path

    Returns:
        True if successful
    """
    try:
        with open(path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


def get_screenshot_from_clipboard() -> Optional[bytes]:
    """Get screenshot from clipboard.

    Returns:
        Image data or None
    """
    # Platform-specific implementation
    return None


def encode_screenshot_base64(data: bytes) -> str:
    """Encode screenshot to base64.

    Args:
        data: Screenshot data

    Returns:
        Base64 string
    """
    return base64.b64encode(data).decode()


__all__ = [
    "capture_screenshot",
    "save_screenshot",
    "get_screenshot_from_clipboard",
    "encode_screenshot_base64",
]