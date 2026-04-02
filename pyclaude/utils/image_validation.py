"""
Image validation utilities.

Validate image files.
"""

from typing import Optional, Tuple


MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_DIMENSION = 4096


def validate_image_size(size: int) -> bool:
    """Validate image size.

    Args:
        size: Image size in bytes

    Returns:
        True if valid
    """
    return 0 < size <= MAX_IMAGE_SIZE


def validate_image_dimensions(width: int, height: int) -> bool:
    """Validate image dimensions.

    Args:
        width: Image width
        height: Image height

    Returns:
        True if valid
    """
    return 0 < width <= MAX_IMAGE_DIMENSION and 0 < height <= MAX_IMAGE_DIMENSION


def is_supported_image_format(filename: str) -> bool:
    """Check if image format is supported.

    Args:
        filename: Image filename

    Returns:
        True if supported
    """
    supported = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]
    ext = filename.lower().split(".")[-1]
    return f".{ext}" in supported


__all__ = [
    "MAX_IMAGE_SIZE",
    "MAX_IMAGE_DIMENSION",
    "validate_image_size",
    "validate_image_dimensions",
    "is_supported_image_format",
]