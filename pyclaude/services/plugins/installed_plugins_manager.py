"""Installed plugins manager.

Manages the installed plugins registry.
Corresponds to src/utils/plugins/installedPluginsManager.ts
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .plugin_directories import get_plugins_directory, get_versioned_cache_path
from .schemas import InstalledPluginsData, PluginInstallation


# ============================================================================
# Constants
# ============================================================================

INSTALLED_PLUGINS_FILE = 'installed_plugins.json'
INSTALLED_PLUGINS_V2_FILE = 'installed_plugins_v2.json'
CURRENT_VERSION = '2'


# ============================================================================
# File Operations
# ============================================================================

def get_installed_plugins_file() -> Path:
    """Get the installed plugins file path."""
    return get_plugins_directory() / INSTALLED_PLUGINS_V2_FILE


def load_installed_plugins_from_disk() -> InstalledPluginsData:
    """Load installed plugins data from disk.

    Returns:
        The installed plugins data structure
    """
    file_path = get_installed_plugins_file()

    if not file_path.exists():
        return {'version': CURRENT_VERSION, 'plugins': {}}

    try:
        with open(file_path) as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {'version': CURRENT_VERSION, 'plugins': {}}
    except (json.JSONDecodeError, IOError):
        return {'version': CURRENT_VERSION, 'plugins': {}}


def save_installed_plugins_to_disk(data: InstalledPluginsData) -> None:
    """Save installed plugins data to disk.

    Args:
        data: The installed plugins data to save
    """
    file_path = get_installed_plugins_file()
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def add_installed_plugin(
    plugin_id: str,
    install_path: str,
    version: str | None = None,
    scope: str = 'user',
    project_path: str | None = None,
    commit_sha: str | None = None,
) -> None:
    """Add a plugin installation record.

    Args:
        plugin_id: The plugin ID
        install_path: The installation path
        version: The plugin version
        scope: The installation scope (user, project, local)
        project_path: The project path (for project/local scopes)
        commit_sha: The Git commit SHA
    """
    data = load_installed_plugins_from_disk()

    if 'plugins' not in data:
        data['plugins'] = {}
    if 'version' not in data:
        data['version'] = CURRENT_VERSION

    if plugin_id not in data['plugins']:
        data['plugins'][plugin_id] = []

    from datetime import datetime
    now = datetime.utcnow().isoformat() + 'Z'

    installation: PluginInstallation = {
        'pluginId': plugin_id,
        'installPath': install_path,
        'version': version,
        'scope': scope,
        'projectPath': project_path,
        'installedAt': now,
        'lastUpdated': now,
    }

    if commit_sha:
        installation['commitSha'] = commit_sha

    # Check if this exact installation already exists
    existing = data['plugins'][plugin_id]
    for i, inst in enumerate(existing):
        if inst.get('scope') == scope and inst.get('projectPath') == project_path:
            # Update existing installation
            existing[i] = installation
            save_installed_plugins_to_disk(data)
            return

    # Add new installation
    data['plugins'][plugin_id].append(installation)
    save_installed_plugins_to_disk(data)


def remove_plugin_installation(
    plugin_id: str,
    scope: str = 'user',
    project_path: str | None = None,
) -> bool:
    """Remove a plugin installation record.

    Args:
        plugin_id: The plugin ID
        scope: The installation scope
        project_path: The project path

    Returns:
        True if an installation was removed
    """
    data = load_installed_plugins_from_disk()

    if not data.get('plugins') or plugin_id not in data['plugins']:
        return False

    installations = data['plugins'][plugin_id]
    original_count = len(installations)

    data['plugins'][plugin_id] = [
        inst for inst in installations
        if inst.get('scope') != scope or inst.get('projectPath') != project_path
    ]

    if len(data['plugins'][plugin_id]) == 0:
        del data['plugins'][plugin_id]

    if len(data['plugins']) == 0:
        # Clean up empty file
        if get_installed_plugins_file().exists():
            get_installed_plugins_file().unlink()
        return original_count > 0

    save_installed_plugins_to_disk(data)
    return len(data['plugins'][plugin_id]) < original_count


def update_installation_path_on_disk(
    plugin_id: str,
    scope: str,
    project_path: str | None,
    new_path: str,
    new_version: str | None = None,
    commit_sha: str | None = None,
) -> None:
    """Update the installation path for a plugin.

    Args:
        plugin_id: The plugin ID
        scope: The installation scope
        project_path: The project path
        new_path: The new installation path
        new_version: The new version
        commit_sha: The new Git commit SHA
    """
    data = load_installed_plugins_from_disk()

    if not data.get('plugins') or plugin_id not in data['plugins']:
        return

    from datetime import datetime
    now = datetime.utcnow().isoformat() + 'Z'

    for inst in data['plugins'][plugin_id]:
        if inst.get('scope') == scope and inst.get('projectPath') == project_path:
            inst['installPath'] = new_path
            if new_version:
                inst['version'] = new_version
            if commit_sha:
                inst['commitSha'] = commit_sha
            inst['lastUpdated'] = now
            break

    save_installed_plugins_to_disk(data)


# ============================================================================
# Query Functions
# ============================================================================

def is_plugin_installed(plugin_id: str) -> bool:
    """Check if a plugin is installed.

    Args:
        plugin_id: The plugin ID to check

    Returns:
        True if the plugin is installed
    """
    data = load_installed_plugins_from_disk()
    return plugin_id in data.get('plugins', {}) and len(data['plugins'][plugin_id]) > 0


def get_plugin_installations(plugin_id: str) -> list[PluginInstallation]:
    """Get all installations of a plugin.

    Args:
        plugin_id: The plugin ID

    Returns:
        List of installation records
    """
    data = load_installed_plugins_from_disk()
    return data.get('plugins', {}).get(plugin_id, [])


def get_plugin_installation_for_scope(
    plugin_id: str,
    scope: str,
    project_path: str | None = None,
) -> PluginInstallation | None:
    """Get a specific plugin installation for a scope.

    Args:
        plugin_id: The plugin ID
        scope: The installation scope
        project_path: The project path

    Returns:
        The installation record or None
    """
    installations = get_plugin_installations(plugin_id)
    for inst in installations:
        if inst.get('scope') == scope and inst.get('projectPath') == project_path:
            return inst
    return None


__all__ = [
    'load_installed_plugins_from_disk',
    'save_installed_plugins_to_disk',
    'add_installed_plugin',
    'remove_plugin_installation',
    'update_installation_path_on_disk',
    'is_plugin_installed',
    'get_plugin_installations',
    'get_plugin_installation_for_scope',
]