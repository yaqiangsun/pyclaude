"""
Windows paths utilities.

Windows path conversion.
"""

import os
from typing import Optional


def windows_path_to_posix_path(path: str) -> str:
    """Convert Windows path to POSIX path.

    Args:
        path: Windows path

    Returns:
        POSIX path
    """
    # Convert C:\foo\bar to /c/foo/bar
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        return "/" + drive + path[2:].replace("\\", "/")
    return path.replace("\\", "/")


def posix_path_to_windows_path(path: str) -> str:
    """Convert POSIX path to Windows path.

    Args:
        path: POSIX path

    Returns:
        Windows path
    """
    # Convert /c/foo/bar to C:\foo\bar
    if len(path) >= 2 and path[0] == "/" and path[1].isalpha():
        drive = path[1].upper()
        return drive + ":\\" + path[3:].replace("/", "\\")
    return path.replace("/", "\\")


def is_windows_path(path: str) -> bool:
    """Check if path is Windows-style.

    Args:
        path: Path to check

    Returns:
        True if Windows path
    """
    return len(path) >= 2 and path[1] == ":"


__all__ = [
    "windows_path_to_posix_path",
    "posix_path_to_windows_path",
    "is_windows_path",
]