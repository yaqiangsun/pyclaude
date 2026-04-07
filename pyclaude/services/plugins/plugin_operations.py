"""Core plugin operations (install, uninstall, enable, disable, update).

Provides pure library functions for plugin operations.
Corresponds to src/services/plugins/pluginOperations.ts
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .installed_plugins_manager import (
    add_installed_plugin,
    get_plugin_installation_for_scope,
    get_plugin_installations,
    load_installed_plugins_from_disk,
    remove_plugin_installation,
    update_installation_path_on_disk,
)
from .marketplace_manager import (
    get_plugin_by_id,
    load_known_marketplaces_config,
    search_plugin_in_marketplaces,
)
from .plugin_directories import (
    get_plugin_cache_dir,
    get_plugins_directory,
    get_versioned_cache_path,
)
from .plugin_identifier import (
    parse_plugin_identifier,
    scope_to_setting_source,
)
from .schemas import PluginInstallation, PluginScope, validate_plugin_name


# ============================================================================
# Types
# ============================================================================

@dataclass
class PluginOperationResult:
    """Result of a plugin operation."""
    success: bool
    message: str
    plugin_id: str | None = None
    plugin_name: str | None = None
    scope: str | None = None
    reverse_dependents: list[str] | None = None


@dataclass
class PluginUpdateResult:
    """Result of a plugin update operation."""
    success: bool
    message: str
    plugin_id: str | None = None
    new_version: str | None = None
    old_version: str | None = None
    already_up_to_date: bool = False
    scope: str | None = None


# ============================================================================
# Constants
# ============================================================================

VALID_INSTALLABLE_SCOPES = ['user', 'project', 'local']
VALID_UPDATE_SCOPES = ['user', 'project', 'local', 'managed']


# ============================================================================
# Helper Functions
# ============================================================================

def get_settings_file_path(scope: str) -> Path:
    """Get the settings file path for a given scope."""
    if scope == 'local':
        # Local settings are in .claude/settings.json in the current directory
        return Path.cwd() / '.claude' / 'settings.json'
    elif scope == 'project':
        # Project settings are in .claude/settings.json at project root
        return Path.cwd() / '.claude' / 'settings.json'
    else:
        # User settings are in ~/.claude/settings.json
        return get_plugins_directory().parent / 'settings.json'


def load_settings(scope: str) -> dict:
    """Load settings for a given scope."""
    settings_file = get_settings_file_path(scope)

    if not settings_file.exists():
        return {}

    try:
        with open(settings_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_settings(scope: str, settings: dict) -> None:
    """Save settings for a given scope."""
    settings_file = get_settings_file_path(scope)
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)


def get_enabled_plugins(scope: str) -> dict:
    """Get enabled plugins for a scope."""
    settings = load_settings(scope)
    return settings.get('enabledPlugins', {})


def set_plugin_enabled(plugin_id: str, enabled: bool, scope: str) -> None:
    """Set plugin enabled state in settings."""
    settings = load_settings(scope)

    if 'enabledPlugins' not in settings:
        settings['enabledPlugins'] = {}

    if enabled:
        settings['enabledPlugins'][plugin_id] = True
    else:
        # Remove the key to disable (or set to False)
        if plugin_id in settings['enabledPlugins']:
            del settings['enabledPlugins'][plugin_id]

    save_settings(scope, settings)


def get_project_path_for_scope(scope: str) -> str | None:
    """Get the project path for scopes that are project-specific."""
    if scope in ('project', 'local'):
        return str(Path.cwd())
    return None


# ============================================================================
# Plugin Install
# ============================================================================

async def install_plugin_op(
    plugin: str,
    scope: str = 'user',
) -> PluginOperationResult:
    """Install a plugin.

    Args:
        plugin: Plugin identifier (name or name@marketplace)
        scope: Installation scope: user, project, or local

    Returns:
        Result indicating success/failure
    """
    if scope not in VALID_INSTALLABLE_SCOPES:
        return PluginOperationResult(
            success=False,
            message=f"Invalid scope '{scope}'. Must be one of: {', '.join(VALID_INSTALLABLE_SCOPES)}",
        )

    parsed = parse_plugin_identifier(plugin)
    plugin_name = parsed.name
    marketplace_name = parsed.marketplace

    # Search for the plugin
    found_plugin = None
    found_marketplace = None
    marketplace_install_location = None

    if marketplace_name:
        # Specific marketplace requested
        plugin_info = await get_plugin_by_id(plugin)
        if plugin_info:
            found_plugin = plugin_info['entry']
            found_marketplace = marketplace_name
            marketplace_install_location = plugin_info.get('marketplaceInstallLocation', '')
    else:
        # Search across all marketplaces
        found_plugin, found_marketplace, marketplace_install_location = await search_plugin_in_marketplaces(plugin_name)

    if not found_plugin or not found_marketplace:
        location = marketplace_name if marketplace_name else 'any configured marketplace'
        return PluginOperationResult(
            success=False,
            message=f'Plugin "{plugin_name}" not found in {location}',
        )

    plugin_id = f"{found_plugin['name']}@{found_marketplace}"

    # Validate plugin name
    valid, error = validate_plugin_name(found_plugin['name'])
    if not valid:
        return PluginOperationResult(
            success=False,
            message=f'Invalid plugin name: {error}',
        )

    # Install the plugin
    try:
        install_result = await install_resolved_plugin(
            plugin_id=plugin_id,
            entry=found_plugin,
            scope=scope,
            marketplace_install_location=marketplace_install_location,
        )

        if not install_result['success']:
            return PluginOperationResult(
                success=False,
                message=install_result.get('message', 'Installation failed'),
            )

        return PluginOperationResult(
            success=True,
            message=install_result['message'],
            plugin_id=plugin_id,
            plugin_name=found_plugin['name'],
            scope=scope,
        )

    except Exception as e:
        return PluginOperationResult(
            success=False,
            message=f'Failed to install plugin: {str(e)}',
        )


async def install_resolved_plugin(
    plugin_id: str,
    entry: dict,
    scope: str,
    marketplace_install_location: str,
) -> dict:
    """Install a resolved plugin from marketplace entry.

    Args:
        plugin_id: The plugin ID
        entry: The plugin marketplace entry
        scope: The installation scope
        marketplace_install_location: The marketplace install location

    Returns:
        Dict with success boolean and message
    """
    from .plugin_loader import cache_plugin, calculate_plugin_version

    source = entry.get('source')

    # For local plugins (string source like "./path")
    if isinstance(source, str):
        source_path = Path(marketplace_install_location).parent / source
    else:
        source_path = None

    # Cache the plugin
    cache_result = await cache_plugin(source, {
        'manifest': entry,
        'source_path': source_path,
    })

    # Calculate version
    version = await calculate_plugin_version(
        plugin_id,
        entry.get('source'),
        entry.get('version'),
        str(source_path) if source_path else cache_result.get('path', ''),
    )

    # Get versioned cache path
    versioned_path = get_versioned_cache_path(plugin_id, version)
    versioned_path.mkdir(parents=True, exist_ok=True)

    # Copy to versioned path
    cache_path = Path(cache_result.get('path', ''))
    if cache_path.exists() and cache_path != versioned_path:
        if cache_path.is_dir():
            if versioned_path.exists():
                shutil.rmtree(versioned_path)
            shutil.copytree(cache_path, versioned_path, symlinks=True)
        else:
            shutil.copy2(cache_path, versioned_path)

    # Add to installed plugins
    project_path = get_project_path_for_scope(scope)
    add_installed_plugin(
        plugin_id=plugin_id,
        install_path=str(versioned_path),
        version=version,
        scope=scope,
        project_path=project_path,
        commit_sha=cache_result.get('git_commit_sha'),
    )

    # Enable in settings
    set_plugin_enabled(plugin_id, True, scope)

    return {
        'success': True,
        'message': f'Successfully installed plugin: {plugin_id} (scope: {scope})',
    }


# ============================================================================
# Plugin Uninstall
# ============================================================================

async def uninstall_plugin_op(
    plugin: str,
    scope: str = 'user',
    delete_data_dir: bool = True,
) -> PluginOperationResult:
    """Uninstall a plugin.

    Args:
        plugin: Plugin name or plugin@marketplace identifier
        scope: Uninstall from scope
        delete_data_dir: Whether to delete plugin data directory

    Returns:
        Result indicating success/failure
    """
    if scope not in VALID_INSTALLABLE_SCOPES:
        return PluginOperationResult(
            success=False,
            message=f"Invalid scope '{scope}'. Must be one of: {', '.join(VALID_INSTALLABLE_SCOPES)}",
        )

    parsed = parse_plugin_identifier(plugin)
    plugin_name = parsed.name
    plugin_id = plugin if '@' in plugin else f"{plugin_name}@unknown"

    # Find plugin installations
    installations = get_plugin_installations(plugin_id)
    project_path = get_project_path_for_scope(scope)

    # Find installation for this scope
    scope_installation = None
    for inst in installations:
        if inst.get('scope') == scope and inst.get('projectPath') == project_path:
            scope_installation = inst
            break

    if not scope_installation:
        # Check where it's actually installed
        if installations:
            actual_scope = installations[0].get('scope', 'unknown')
            return PluginOperationResult(
                success=False,
                message=f'Plugin "{plugin}" is installed in {actual_scope} scope, not {scope}. Use --scope {actual_scope} to uninstall.',
            )
        return PluginOperationResult(
            success=False,
            message=f'Plugin "{plugin}" is not installed in {scope} scope',
        )

    # Remove from settings
    set_plugin_enabled(plugin_id, False, scope)

    # Remove installation record
    remove_plugin_installation(plugin_id, scope, project_path)

    # Note: We don't delete the cached files by default to allow for offline access

    return PluginOperationResult(
        success=True,
        message=f'Successfully uninstalled plugin: {plugin_name} (scope: {scope})',
        plugin_id=plugin_id,
        plugin_name=plugin_name,
        scope=scope,
    )


# ============================================================================
# Plugin Enable/Disable
# ============================================================================

async def enable_plugin_op(plugin: str, scope: str | None = None) -> PluginOperationResult:
    """Enable a plugin.

    Args:
        plugin: Plugin name or plugin@marketplace identifier
        scope: Optional scope. If not provided, finds the most specific scope.

    Returns:
        Result indicating success/failure
    """
    return await set_plugin_enabled_op(plugin, True, scope)


async def disable_plugin_op(plugin: str, scope: str | None = None) -> PluginOperationResult:
    """Disable a plugin.

    Args:
        plugin: Plugin name or plugin@marketplace identifier
        scope: Optional scope. If not provided, finds the most specific scope.

    Returns:
        Result indicating success/failure
    """
    return await set_plugin_enabled_op(plugin, False, scope)


async def set_plugin_enabled_op(
    plugin: str,
    enabled: bool,
    scope: str | None = None,
) -> PluginOperationResult:
    """Set plugin enabled/disabled state.

    Args:
        plugin: Plugin name or plugin@marketplace identifier
        enabled: True to enable, False to disable
        scope: Optional scope

    Returns:
        Result indicating success/failure
    """
    operation = 'enable' if enabled else 'disable'
    parsed = parse_plugin_identifier(plugin)
    plugin_name = parsed.name

    # Find plugin ID and resolve scope
    if scope:
        if scope not in VALID_INSTALLABLE_SCOPES:
            return PluginOperationResult(
                success=False,
                message=f"Invalid scope '{scope}'. Must be one of: {', '.join(VALID_INSTALLABLE_SCOPES)}",
            )
        resolved_scope = scope
        # Try to find plugin ID in settings
        plugin_id = None
        for s in ['local', 'project', 'user']:
            enabled_plugins = get_enabled_plugins(s)
            for key in enabled_plugins:
                if key == plugin or key.startswith(f"{plugin_name}@"):
                    plugin_id = key
                    if not scope:
                        resolved_scope = s
                    break
            if plugin_id:
                break

        if not plugin_id:
            plugin_id = plugin if '@' in plugin else f"{plugin_name}@{parsed.marketplace or 'unknown'}"
    else:
        # Auto-detect scope
        plugin_id = None
        resolved_scope = 'user'

        for s in ['local', 'project', 'user']:
            enabled_plugins = get_enabled_plugins(s)
            for key in enabled_plugins:
                if key == plugin or key.startswith(f"{plugin_name}@"):
                    plugin_id = key
                    resolved_scope = s
                    break
            if plugin_id:
                break

        if not plugin_id:
            plugin_id = plugin if '@' in plugin else f"{plugin_name}@{parsed.marketplace or 'unknown'}"

    # Check current state
    current_state = get_enabled_plugins(resolved_scope).get(plugin_id, False)
    if current_state == enabled:
        scope_desc = f" at {resolved_scope}" if resolved_scope != 'user' else ""
        return PluginOperationResult(
            success=False,
            message=f'Plugin "{plugin}" is already {"enabled" if enabled else "disabled"}{scope_desc}',
        )

    # Update settings
    set_plugin_enabled(plugin_id, enabled, resolved_scope)

    return PluginOperationResult(
        success=True,
        message=f'Successfully {"enabled" if enabled else "disabled"} plugin: {plugin_name} (scope: {resolved_scope})',
        plugin_id=plugin_id,
        plugin_name=plugin_name,
        scope=resolved_scope,
    )


async def disable_all_plugins_op() -> PluginOperationResult:
    """Disable all enabled plugins.

    Returns:
        Result with count of disabled plugins
    """
    disabled = []
    errors = []

    for scope in ['local', 'project', 'user']:
        enabled_plugins = get_enabled_plugins(scope)
        for plugin_id in list(enabled_plugins.keys()):
            result = await set_plugin_enabled_op(plugin_id, False, scope)
            if result.success:
                disabled.append(plugin_id)
            else:
                errors.append(f"{plugin_id}: {result.message}")

    if errors:
        return PluginOperationResult(
            success=False,
            message=f"Disabled {len(disabled)} plugins, {len(errors)} failed:\n" + '\n'.join(errors),
        )

    return PluginOperationResult(
        success=True,
        message=f'Disabled {len(disabled)} plugins',
    )


# ============================================================================
# Plugin Update
# ============================================================================

async def update_plugin_op(plugin: str, scope: str = 'user') -> PluginUpdateResult:
    """Update a plugin to the latest version.

    Args:
        plugin: Plugin name or plugin@marketplace identifier
        scope: The scope to update

    Returns:
        Result with version info
    """
    if scope not in VALID_UPDATE_SCOPES:
        return PluginUpdateResult(
            success=False,
            message=f"Invalid scope '{scope}'. Must be one of: {', '.join(VALID_UPDATE_SCOPES)}",
        )

    parsed = parse_plugin_identifier(plugin)
    plugin_name = parsed.name

    # Get plugin info from marketplace
    plugin_id = f"{plugin_name}@{parsed.marketplace}" if parsed.marketplace else plugin
    plugin_info = await get_plugin_by_id(plugin_id)

    if not plugin_info:
        return PluginUpdateResult(
            success=False,
            message=f'Plugin "{plugin_name}" not found',
            plugin_id=plugin_id,
            scope=scope,
        )

    entry = plugin_info['entry']
    marketplace_install_location = plugin_info.get('marketplaceInstallLocation', '')

    # Get current installation
    project_path = get_project_path_for_scope(scope)
    installation = get_plugin_installation_for_scope(plugin_id, scope, project_path)

    if not installation:
        return PluginUpdateResult(
            success=False,
            message=f'Plugin "{plugin_name}" is not installed at scope {scope}',
            plugin_id=plugin_id,
            scope=scope,
        )

    old_version = installation.get('version')

    # Get new version from marketplace
    new_version = entry.get('version', old_version)

    if old_version == new_version:
        return PluginUpdateResult(
            success=True,
            message=f'{plugin_name} is already at the latest version ({new_version}).',
            plugin_id=plugin_id,
            new_version=new_version,
            old_version=old_version,
            already_up_to_date=True,
            scope=scope,
        )

    # Re-install to update
    install_result = await install_resolved_plugin(
        plugin_id=plugin_id,
        entry=entry,
        scope=scope,
        marketplace_install_location=marketplace_install_location,
    )

    if not install_result['success']:
        return PluginUpdateResult(
            success=False,
            message=install_result.get('message', 'Update failed'),
            plugin_id=plugin_id,
            scope=scope,
        )

    return PluginUpdateResult(
        success=True,
        message=f'Plugin "{plugin_name}" updated from {old_version or "unknown"} to {new_version} for scope {scope}.',
        plugin_id=plugin_id,
        new_version=new_version,
        old_version=old_version,
        scope=scope,
    )


__all__ = [
    'PluginOperationResult',
    'PluginUpdateResult',
    'VALID_INSTALLABLE_SCOPES',
    'VALID_UPDATE_SCOPES',
    'install_plugin_op',
    'uninstall_plugin_op',
    'enable_plugin_op',
    'disable_plugin_op',
    'set_plugin_enabled_op',
    'disable_all_plugins_op',
    'update_plugin_op',
]