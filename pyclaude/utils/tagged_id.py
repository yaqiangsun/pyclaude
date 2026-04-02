"""
Tagged ID utilities.

Generate and parse tagged identifiers.
"""

import hashlib
from typing import Optional, Tuple
import base64


def create_tagged_id(tag: str, data: str) -> str:
    """Create a tagged ID.

    Args:
        tag: Tag prefix
        data: Data to tag

    Returns:
        Tagged ID
    """
    hash_part = hashlib.sha256(data.encode()).hexdigest()[:12]
    return f"{tag}_{hash_part}"


def parse_tagged_id(tagged_id: str) -> Optional[Tuple[str, str]]:
    """Parse a tagged ID.

    Args:
        tagged_id: Tagged ID

    Returns:
        (tag, hash) or None
    """
    parts = tagged_id.split("_", 1)
    if len(parts) == 2:
        return (parts[0], parts[1])
    return None


def is_tagged_id(tag: str, tagged_id: str) -> bool:
    """Check if ID has specific tag.

    Args:
        tag: Expected tag
        tagged_id: Tagged ID

    Returns:
        True if matches
    """
    parsed = parse_tagged_id(tagged_id)
    return parsed is not None and parsed[0] == tag


__all__ = [
    "create_tagged_id",
    "parse_tagged_id",
    "is_tagged_id",
]