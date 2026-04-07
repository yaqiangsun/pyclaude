"""Built-in Plugin Registry."""
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass

from pyclaude.utils.settings import get_user_claude_settings_path, load_json_file

BUILTIN_MARKETPLACE_NAME = 'builtin'

# Global registry for built-in plugins
_BUILTIN_PLUGINS: dict[str, Any] = {}


@dataclass
class LoadedPlugin:
    """Represents a loaded plugin."""
    name: str
    manifest: dict
    path: str
    source: str
    repository: str
    enabled: bool
    is_builtin: bool
    hooks_config: Optional[dict] = None
    mcp_servers: Optional[list] = None


def register_builtin_plugin(definition: dict) -> None:
    """Register a built-in plugin."""
    _BUILTIN_PLUGINS[definition['name']] = definition


def is_builtin_plugin_id(plugin_id: str) -> bool:
    """Check if plugin ID is a built-in plugin."""
    return plugin_id.endswith(f'@{BUILTIN_MARKETPLACE_NAME}')


def get_builtin_plugin_definition(name: str) -> Optional[dict]:
    """Get a specific built-in plugin definition."""
    return _BUILTIN_PLUGINS.get(name)


def _load_enabled_plugins_from_settings() -> dict[str, bool]:
    """Load enabled plugins from user settings."""
    settings_path = get_user_claude_settings_path()
    settings = load_json_file(settings_path) or {}
    return settings.get('enabledPlugins', {})


def get_builtin_plugins() -> dict[str, list]:
    """Get all registered built-in plugins, split into enabled/disabled based on user settings.

    Returns:
        dict with 'enabled' and 'disabled' lists of LoadedPlugin objects
    """
    enabled = []
    disabled = []

    # Load user settings for enabled plugins
    user_enabled = _load_enabled_plugins_from_settings()

    for name, definition in _BUILTIN_PLUGINS.items():
        # Check isAvailable if present
        if 'isAvailable' in definition:
            is_available = definition['isAvailable']
            if callable(is_available) and not is_available():
                continue

        plugin_id = f'{name}@{BUILTIN_MARKETPLACE_NAME}'
        user_setting = user_enabled.get(plugin_id)

        # Enabled state: user preference > plugin default > true
        is_enabled = user_setting if user_setting is not None else definition.get('defaultEnabled', True)

        manifest = {
            'name': name,
            'description': definition.get('description', ''),
            'version': definition.get('version', '1.0.0'),
        }

        plugin = LoadedPlugin(
            name=name,
            manifest=manifest,
            path=BUILTIN_MARKETPLACE_NAME,  # sentinel — no filesystem path
            source=plugin_id,
            repository=plugin_id,
            enabled=is_enabled,
            is_builtin=True,
            hooks_config=definition.get('hooks'),
            mcp_servers=definition.get('mcpServers'),
        )

        if is_enabled:
            enabled.append(plugin)
        else:
            disabled.append(plugin)

    return {'enabled': enabled, 'disabled': disabled}


def get_builtin_plugin_skill_commands() -> list:
    """Get skills from enabled built-in plugins."""
    result = get_builtin_plugins()
    skills = []

    # TODO: Extract skills from enabled built-in plugins
    # This would require loading the actual skill content from the plugin

    return skills


def clear_builtin_plugins() -> None:
    """Clear built-in plugins registry."""
    _BUILTIN_PLUGINS.clear()


__all__ = [
    'BUILTIN_MARKETPLACE_NAME',
    'register_builtin_plugin',
    'is_builtin_plugin_id',
    'get_builtin_plugin_definition',
    'get_builtin_plugins',
    'get_builtin_plugin_skill_commands',
    'clear_builtin_plugins',
    'LoadedPlugin',
]


def clear_builtin_plugins() -> None:
    """Clear built-in plugins registry."""
    _BUILTIN_PLUGINS.clear()


__all__ = [
    'BUILTIN_MARKETPLACE_NAME',
    'register_builtin_plugin',
    'is_builtin_plugin_id',
    'get_builtin_plugin_definition',
    'get_builtin_plugins',
    'get_builtin_plugin_skill_commands',
    'clear_builtin_plugins',
]