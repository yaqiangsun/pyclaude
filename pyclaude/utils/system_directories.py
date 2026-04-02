"""
System directories utilities.

Get standard system directories.
"""

import os
from pathlib import Path
from typing import Optional


def get_home_dir() -> str:
    """Get user home directory.

    Returns:
        Home directory path
    """
    return str(Path.home())


def get_config_dir() -> str:
    """Get config directory.

    Returns:
        Config directory path
    """
    if os.name == "nt":
        return os.environ.get("APPDATA", "")
    return os.environ.get("XDG_CONFIG_HOME", os.path.join(get_home_dir(), ".config"))


def get_data_dir() -> str:
    """Get data directory.

    Returns:
        Data directory path
    """
    if os.name == "nt":
        return os.environ.get("LOCALAPPDATA", "")
    return os.environ.get("XDG_DATA_HOME", os.path.join(get_home_dir(), ".local", "share"))


def get_cache_dir() -> str:
    """Get cache directory.

    Returns:
        Cache directory path
    """
    if os.name == "nt":
        return os.path.join(get_data_dir(), "Cache")
    return os.environ.get("XDG_CACHE_HOME", os.path.join(get_home_dir(), ".cache"))


def get_temp_dir() -> str:
    """Get temp directory.

    Returns:
        Temp directory path
    """
    import tempfile
    return tempfile.gettempdir()


def get_runtime_dir() -> Optional[str]:
    """Get runtime directory.

    Returns:
        Runtime directory path or None
    """
    if os.name == "nt":
        return None
    return os.environ.get("XDG_RUNTIME_HOME")


__all__ = [
    "get_home_dir",
    "get_config_dir",
    "get_data_dir",
    "get_cache_dir",
    "get_temp_dir",
    "get_runtime_dir",
]