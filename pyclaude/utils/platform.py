"""
Platform utilities.

Platform detection and handling.
"""

import platform
import os
from typing import Optional
from enum import Enum


class Platform(str, Enum):
    """Platform types."""
    DARWIN = "darwin"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


def get_platform() -> Platform:
    """Get current platform.

    Returns:
        Platform enum
    """
    system = platform.system().lower()
    if system == "darwin":
        return Platform.DARWIN
    elif system == "linux":
        return Platform.LINUX
    elif system == "windows":
        return Platform.WINDOWS
    return Platform.UNKNOWN


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == Platform.DARWIN


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == Platform.LINUX


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == Platform.WINDOWS


def get_os_version() -> str:
    """Get OS version string."""
    return platform.release()


def get_architecture() -> str:
    """Get system architecture."""
    return platform.machine()


__all__ = [
    "Platform",
    "get_platform",
    "is_macos",
    "is_linux",
    "is_windows",
    "get_os_version",
    "get_architecture",
]