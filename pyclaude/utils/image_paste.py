"""
Image paste utilities.

Image paste handling.
"""

from typing import Optional, Dict, Any


def is_image_paste(data: bytes) -> bool:
    """Check if data is an image.

    Args:
        data: Binary data

    Returns:
        True if image
    """
    # Check for common image headers
    signatures = [
        b"\x89PNG\r\n\x1a\n",  # PNG
        b"\xff\xd8\xff",  # JPEG
        b"GIF87a",  # GIF
        b"GIF89a",  # GIF
    ]
    return any(data.startswith(sig) for sig in signatures)


def get_image_type(data: bytes) -> Optional[str]:
    """Get image MIME type.

    Args:
        data: Image data

    Returns:
        MIME type or None
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"GIF"):
        return "image/gif"
    return None


__all__ = [
    "is_image_paste",
    "get_image_type",
]