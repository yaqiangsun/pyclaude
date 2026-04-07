"""Plugin schemas and types.

Provides type definitions and validation for plugins and marketplaces.
Corresponds to src/utils/plugins/schemas.ts
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


# ============================================================================
# Constants
# ============================================================================

ALLOWED_OFFICIAL_MARKETPLACE_NAMES = {
    'claude-code-marketplace',
    'claude-code-plugins',
    'claude-plugins-official',
    'anthropic-marketplace',
    'anthropic-plugins',
    'agent-skills',
    'life-sciences',
    'knowledge-work-plugins',
}

NO_AUTO_UPDATE_OFFICIAL_MARKETPLACES = {'knowledge-work-plugins'}

OFFICIAL_GITHUB_ORG = 'anthropics'

BLOCKED_OFFICIAL_NAME_PATTERN = re.compile(
    r'(?:official[^a-z0-9]*(anthropic|claude)|(?:anthropic|claude)[^a-z0-9]*official|^(?:anthropic|claude)[^a-z0-9]*(marketplace|plugins|official))',
    re.IGNORECASE,
)

NON_ASCII_PATTERN = re.compile(r'[^\x20-\x7e]')


# ============================================================================
# Schema Functions
# ============================================================================

def is_blocked_official_name(name: str) -> bool:
    """Check if a marketplace name impersonates an official Anthropic/Claude marketplace."""
    if name.lower() in ALLOWED_OFFICIAL_MARKETPLACE_NAMES:
        return False
    if NON_ASCII_PATTERN.search(name):
        return True
    return bool(BLOCKED_OFFICIAL_NAME_PATTERN.search(name))


def is_marketplace_auto_update(marketplace_name: str, entry: Optional[dict] = None) -> bool:
    """Check if auto-update is enabled for a marketplace."""
    if entry and 'autoUpdate' in entry:
        return entry['autoUpdate']
    normalized = marketplace_name.lower()
    return (
        normalized in ALLOWED_OFFICIAL_MARKETPLACE_NAMES
        and normalized not in NO_AUTO_UPDATE_OFFICIAL_MARKETPLACES
    )


def validate_official_name_source(name: str, source: dict) -> Optional[str]:
    """Validate that a marketplace with a reserved name comes from the official source."""
    normalized_name = name.lower()

    if normalized_name not in ALLOWED_OFFICIAL_MARKETPLACE_NAMES:
        return None

    source_type = source.get('source')
    if source_type == 'github':
        repo = source.get('repo', '')
        if not repo.lower().startswith(f'{OFFICIAL_GITHUB_ORG}/'):
            return f"The name '{name}' is reserved for official Anthropic marketplaces. Only repositories from 'github.com/{OFFICIAL_GITHUB_ORG}/' can use this name."
        return None

    if source_type == 'git':
        url = source.get('url', '').lower()
        if 'github.com/anthropics/' in url or 'git@github.com:anthropics/' in url:
            return None
        return f"The name '{name}' is reserved for official Anthropic marketplaces. Only repositories from 'github.com/{OFFICIAL_GITHUB_ORG}/' can use this name."

    return f"The name '{name}' is reserved for official Anthropic marketplaces and can only be used with GitHub sources from the '{OFFICIAL_GITHUB_ORG}' organization."


# ============================================================================
# TypedDicts
# ============================================================================

class PluginAuthor(TypedDict, total=False):
    """Plugin author information."""
    name: str
    email: str
    url: str


class DependencyRef(TypedDict, total=False):
    """Plugin dependency reference."""
    name: str
    marketplace: str


class CommandMetadata(TypedDict, total=False):
    """Command metadata."""
    source: str
    content: str
    description: str
    argumentHint: str


class AgentMetadata(TypedDict, total=False):
    """Agent metadata."""
    source: str
    content: str
    description: str
    argumentHint: str


class HooksConfig(TypedDict, total=False):
    """Hooks configuration."""
    description: str
    hooks: dict


class McpServerConfig(TypedDict, total=False):
    """MCP server configuration."""
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str


class LspServerConfig(TypedDict, total=False):
    """LSP server configuration."""
    command: str
    args: List[str]
    env: Dict[str, str]


class PluginManifest(TypedDict, total=False):
    """Plugin manifest."""
    name: str
    version: str
    description: str
    author: PluginAuthor
    homepage: str
    repository: str
    license: str
    keywords: List[str]
    dependencies: List[DependencyRef]
    commands: Dict[str, CommandMetadata]
    agents: Dict[str, AgentMetadata]
    hooks: Union[HooksConfig, List[str], List[dict]]
    mcp_servers: Dict[str, McpServerConfig]
    lsp_servers: Dict[str, LspServerConfig]
    settings: Dict[str, Any]


class PluginSourceGit(TypedDict):
    """Git source for a plugin."""
    source: str  # 'git'
    url: str
    ref: Optional[str]
    subdir: Optional[str]


class PluginSourceNpm(TypedDict):
    """NPM source for a plugin."""
    source: str  # 'npm'
    package: str


class PluginSourceDirectory(TypedDict):
    """Directory source for a plugin."""
    source: str  # 'directory'
    path: str


class PluginSourceFile(TypedDict):
    """File source for a plugin."""
    source: str  # 'file'
    path: str


# Type alias for plugin source
PluginSource = Union[str, PluginSourceGit, PluginSourceNpm, PluginSourceDirectory, PluginSourceFile]


class PluginMarketplaceEntry(TypedDict, total=False):
    """Plugin entry in a marketplace."""
    name: str
    description: str
    version: str
    author: PluginAuthor
    homepage: str
    repository: str
    keywords: List[str]
    source: PluginSource
    commands: Dict[str, CommandMetadata]
    agents: Dict[str, AgentMetadata]
    hooks: Union[HooksConfig, List[str], List[dict]]
    mcp_servers: Dict[str, McpServerConfig]
    lsp_servers: Dict[str, LspServerConfig]
    settings: Dict[str, Any]
    dependencies: List[DependencyRef]


class MarketplaceSourceGit(TypedDict):
    """Git source for a marketplace."""
    source: str  # 'git'
    url: str
    ref: Optional[str]
    sparsePaths: Optional[List[str]]


class MarketplaceSourceGithub(TypedDict):
    """GitHub source for a marketplace."""
    source: str  # 'github'
    repo: str
    ref: Optional[str]
    sparsePaths: Optional[List[str]]


class MarketplaceSourceUrl(TypedDict):
    """URL source for a marketplace."""
    source: str  # 'url'
    url: str


class MarketplaceSourceNpm(TypedDict):
    """NPM source for a marketplace."""
    source: str  # 'npm'
    package: str


class MarketplaceSourceDirectory(TypedDict):
    """Directory source for a marketplace."""
    source: str  # 'directory'
    path: str


class MarketplaceSourceFile(TypedDict):
    """File source for a marketplace."""
    source: str  # 'file'
    path: str


class MarketplaceSourceSettings(TypedDict):
    """Settings source for a marketplace (inline plugins)."""
    source: str  # 'settings'
    name: str
    plugins: List[PluginMarketplaceEntry]


# Type alias for marketplace source
MarketplaceSource = Union[
    MarketplaceSourceGit,
    MarketplaceSourceGithub,
    MarketplaceSourceUrl,
    MarketplaceSourceNpm,
    MarketplaceSourceDirectory,
    MarketplaceSourceFile,
    MarketplaceSourceSettings,
]


class KnownMarketplace(TypedDict, total=False):
    """Known marketplace configuration."""
    source: MarketplaceSource
    installLocation: str
    lastUpdated: str
    autoUpdate: bool


class KnownMarketplacesFile(TypedDict, total=False):
    """Known marketplaces configuration file."""
    pass


class PluginInstallation(TypedDict, total=False):
    """Plugin installation record."""
    pluginId: str
    installPath: str
    version: Optional[str]
    scope: str
    projectPath: Optional[str]
    installedAt: Optional[str]
    lastUpdated: Optional[str]
    commitSha: Optional[str]


class InstalledPluginsData(TypedDict, total=False):
    """Installed plugins data structure."""
    version: str
    plugins: Dict[str, List[PluginInstallation]]


# ============================================================================
# Enums
# ============================================================================

class PluginScope:
    """Plugin installation scope."""
    USER = 'user'
    PROJECT = 'project'
    LOCAL = 'local'
    MANAGED = 'managed'

    ALL = [USER, PROJECT, LOCAL, MANAGED]
    EDITABLE = [USER, PROJECT, LOCAL]


# ============================================================================
# Validation Functions
# ============================================================================

def validate_marketplace_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate marketplace name."""
    if not name:
        return False, 'Marketplace must have a name'

    if ' ' in name:
        return False, 'Marketplace name cannot contain spaces. Use kebab-case (e.g., "my-marketplace")'

    if '/' in name or '\\' in name or '..' in name or name == '.':
        return False, 'Marketplace name cannot contain path separators (/ or \\), ".." sequences, or be "."'

    if is_blocked_official_name(name):
        return False, 'Marketplace name impersonates an official Anthropic/Claude marketplace'

    if name.lower() == 'inline':
        return False, 'Marketplace name "inline" is reserved for --plugin-dir session plugins'

    if name.lower() == 'builtin':
        return False, 'Marketplace name "builtin" is reserved for built-in plugins'

    return True, None


def validate_plugin_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate plugin name."""
    if not name:
        return False, 'Plugin name cannot be empty'

    if ' ' in name:
        return False, 'Plugin name cannot contain spaces. Use kebab-case (e.g., "my-plugin")'

    return True, None


__all__ = [
    'ALLOWED_OFFICIAL_MARKETPLACE_NAMES',
    'NO_AUTO_UPDATE_OFFICIAL_MARKETPLACES',
    'OFFICIAL_GITHUB_ORG',
    'PluginAuthor',
    'DependencyRef',
    'CommandMetadata',
    'AgentMetadata',
    'HooksConfig',
    'McpServerConfig',
    'LspServerConfig',
    'PluginManifest',
    'PluginSource',
    'PluginSourceGit',
    'PluginSourceNpm',
    'PluginSourceDirectory',
    'PluginSourceFile',
    'PluginMarketplaceEntry',
    'MarketplaceSource',
    'MarketplaceSourceGit',
    'MarketplaceSourceGithub',
    'MarketplaceSourceUrl',
    'MarketplaceSourceNpm',
    'MarketplaceSourceDirectory',
    'MarketplaceSourceFile',
    'MarketplaceSourceSettings',
    'KnownMarketplace',
    'KnownMarketplacesFile',
    'PluginInstallation',
    'InstalledPluginsData',
    'PluginScope',
    'validate_marketplace_name',
    'validate_plugin_name',
    'is_blocked_official_name',
    'is_marketplace_auto_update',
    'validate_official_name_source',
]