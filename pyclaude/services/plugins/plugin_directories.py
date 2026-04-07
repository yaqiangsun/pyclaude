"""Plugin directories management.

Provides functions to manage plugin directories and paths.
Corresponds to src/utils/plugins/pluginDirectories.ts
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


# ============================================================================
# Directory Paths
# ============================================================================

def get_plugins_directory() -> Path:
    """Get the plugins directory path (~/.claude/plugins)."""
    return Path.home() / '.claude' / 'plugins'


def get_marketplaces_cache_dir() -> Path:
    """Get the marketplaces cache directory."""
    return get_plugins_directory() / 'marketplaces'


def get_plugin_cache_dir() -> Path:
    """Get the plugin cache directory."""
    return get_plugins_directory() / 'cache'


def get_plugin_seed_dirs() -> list[Path]:
    """Get plugin seed directories (read-only pre-configured plugin sources).

    Returns empty list by default - can be overridden in specific environments.
    """
    return []


def get_plugin_data_dir(plugin_id: str) -> Path:
    """Get the data directory for a specific plugin.

    Args:
        plugin_id: The plugin ID

    Returns:
        Path to the plugin's data directory
    """
    # Sanitize plugin_id for use as directory name
    safe_id = plugin_id.replace('@', '_').replace('/', '_').replace('\\', '_')
    return get_plugins_directory() / 'data' / safe_id


def ensure_plugin_dirs() -> None:
    """Ensure all required plugin directories exist."""
    get_plugins_directory().mkdir(parents=True, exist_ok=True)
    get_marketplaces_cache_dir().mkdir(parents=True, exist_ok=True)
    get_plugin_cache_dir().mkdir(parents=True, exist_ok=True)


# ============================================================================
# Installation Paths
# ============================================================================

def get_versioned_cache_path(plugin_id: str, version: str) -> Path:
    """Get the versioned cache path for a plugin.

    Args:
        plugin_id: The plugin ID
        version: The plugin version

    Returns:
        Path to the versioned cache directory
    """
    # Sanitize plugin_id for use as directory name
    safe_id = plugin_id.replace('@', '_').replace('/', '_').replace('\\', '_')
    return get_plugin_cache_dir() / safe_id / version


def get_versioned_zip_cache_path(plugin_id: str, version: str) -> Path:
    """Get the versioned zip cache path for a plugin.

    Args:
        plugin_id: The plugin ID
        version: The plugin version

    Returns:
        Path to the versioned zip cache file
    """
    return get_versioned_cache_path(plugin_id, version).with_suffix('.zip')


__all__ = [
    'get_plugins_directory',
    'get_marketplaces_cache_dir',
    'get_plugin_cache_dir',
    'get_plugin_seed_dirs',
    'get_plugin_data_dir',
    'ensure_plugin_dirs',
    'get_versioned_cache_path',
    'get_versioned_zip_cache_path',
]