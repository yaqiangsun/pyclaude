"""
Image resizer utilities.

Image resizing for display.
"""

from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ImageDimensions:
    """Image dimensions."""
    width: int
    height: int


def resize_image(
    width: int,
    height: int,
    max_width: int = 800,
    max_height: int = 600,
) -> Tuple[int, int]:
    """Resize image to fit within bounds.

    Args:
        width: Original width
        height: Original height
        max_width: Max width
        max_height: Max height

    Returns:
        (new_width, new_height)
    """
    if width <= max_width and height <= max_height:
        return (width, height)

    ratio = min(max_width / width, max_height / height)
    return (int(width * ratio), int(height * ratio))


def calculate_aspect_ratio(width: int, height: int) -> float:
    """Calculate aspect ratio.

    Args:
        width: Width
        height: Height

    Returns:
        Aspect ratio
    """
    return width / height if height > 0 else 1.0


__all__ = [
    "ImageDimensions",
    "resize_image",
    "calculate_aspect_ratio",
]