"""Plugin identifier parsing utilities.

Provides functions to parse and build plugin identifiers.
Corresponds to src/utils/plugins/pluginIdentifier.ts
"""
from __future__ import annotations

from dataclasses import dataclass


# ============================================================================
# Types
# ============================================================================

@dataclass(frozen=True)
class ParsedPluginIdentifier:
    """Parsed plugin identifier with name and optional marketplace."""
    name: str
    marketplace: str | None = None


# ============================================================================
# Constants
# ============================================================================

SETTING_SOURCE_TO_SCOPE = {
    'policySettings': 'managed',
    'userSettings': 'user',
    'projectSettings': 'project',
    'localSettings': 'local',
    'flagSettings': 'flag',
}

SCOPE_TO_EDITABLE_SOURCE = {
    'user': 'userSettings',
    'project': 'projectSettings',
    'local': 'localSettings',
}


# ============================================================================
# Functions
# ============================================================================

def parse_plugin_identifier(plugin: str) -> ParsedPluginIdentifier:
    """Parse a plugin identifier string into name and marketplace components.

    Args:
        plugin: The plugin identifier (name or name@marketplace)

    Returns:
        ParsedPluginIdentifier with name and optional marketplace

    Note:
        Only the first '@' is used as separator. If the input contains multiple '@'
        symbols (e.g., "plugin@market@place"), everything after the second '@' is ignored.
    """
    if '@' in plugin:
        parts = plugin.split('@', 1)
        return ParsedPluginIdentifier(name=parts[0], marketplace=parts[1])
    return ParsedPluginIdentifier(name=plugin, marketplace=None)


def build_plugin_id(name: str, marketplace: str | None = None) -> str:
    """Build a plugin ID from name and marketplace.

    Args:
        name: The plugin name
        marketplace: Optional marketplace name

    Returns:
        Plugin ID in format "name" or "name@marketplace"
    """
    if marketplace:
        return f"{name}@{marketplace}"
    return name


def is_official_marketplace_name(marketplace: str | None) -> bool:
    """Check if a marketplace name is an official (Anthropic-controlled) marketplace.

    Args:
        marketplace: The marketplace name to check

    Returns:
        True if it's an official marketplace
    """
    from .schemas import ALLOWED_OFFICIAL_MARKETPLACE_NAMES

    if marketplace is None:
        return False
    return marketplace.lower() in ALLOWED_OFFICIAL_MARKETPLACE_NAMES


def scope_to_setting_source(scope: str) -> str:
    """Convert a plugin scope to its corresponding editable setting source.

    Args:
        scope: The plugin installation scope

    Returns:
        The corresponding setting source

    Raises:
        ValueError: If scope is 'managed' (cannot install plugins to managed scope)
    """
    if scope == 'managed':
        raise ValueError('Cannot install plugins to managed scope')
    return SCOPE_TO_EDITABLE_SOURCE.get(scope, 'userSettings')


def setting_source_to_scope(source: str) -> str:
    """Convert an editable setting source to its corresponding plugin scope.

    Args:
        source: The setting source

    Returns:
        The corresponding plugin scope
    """
    return SETTING_SOURCE_TO_SCOPE.get(source, 'user')


__all__ = [
    'ParsedPluginIdentifier',
    'SETTING_SOURCE_TO_SCOPE',
    'SCOPE_TO_EDITABLE_SOURCE',
    'parse_plugin_identifier',
    'build_plugin_id',
    'is_official_marketplace_name',
    'scope_to_setting_source',
    'setting_source_to_scope',
]