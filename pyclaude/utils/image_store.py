"""
Image store utilities.

Image storage and retrieval.
"""

import os
import hashlib
from typing import Optional
from pathlib import Path


def get_image_store_path(image_id: str) -> str:
    """Get path for stored image.

    Args:
        image_id: Image identifier

    Returns:
        Storage path
    """
    cache_dir = os.environ.get("CLAUDE_CODE_CACHE_DIR", "/tmp/claude-images")
    return os.path.join(cache_dir, f"{image_id}.png")


def store_image(image_id: str, data: bytes) -> bool:
    """Store image data.

    Args:
        image_id: Image identifier
        data: Image data

    Returns:
        True if successful
    """
    try:
        path = get_image_store_path(image_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


def load_image(image_id: str) -> Optional[bytes]:
    """Load stored image.

    Args:
        image_id: Image identifier

    Returns:
        Image data or None
    """
    try:
        path = get_image_store_path(image_id)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
    except Exception:
        pass
    return None


def compute_image_hash(data: bytes) -> str:
    """Compute hash of image data.

    Args:
        data: Image data

    Returns:
        Hash string
    """
    return hashlib.sha256(data).hexdigest()[:16]


__all__ = [
    "get_image_store_path",
    "store_image",
    "load_image",
    "compute_image_hash",
]