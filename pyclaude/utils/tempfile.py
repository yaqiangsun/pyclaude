"""
Tempfile utilities.

Temporary file handling.
"""

import os
import tempfile
from typing import Optional
from pathlib import Path


def create_temp_file(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
) -> str:
    """Create a temporary file.

    Args:
        suffix: File suffix
        prefix: File prefix

    Returns:
        Path to temp file
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    return path


def create_temp_dir(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
) -> str:
    """Create a temporary directory.

    Args:
        suffix: Dir suffix
        prefix: Dir prefix

    Returns:
        Path to temp dir
    """
    return tempfile.mkdtemp(suffix=suffix, prefix=prefix)


def get_temp_dir() -> str:
    """Get temp directory.

    Returns:
        Temp dir path
    """
    return tempfile.gettempdir()


__all__ = [
    "create_temp_file",
    "create_temp_dir",
    "get_temp_dir",
]