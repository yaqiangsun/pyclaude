"""Marketplace manager for Claude Code plugins.

Provides functionality to:
- Manage known marketplace sources (URLs, GitHub repos, npm packages, local files)
- Cache marketplace manifests locally for offline access
- Install plugins from marketplace entries
- Track and update marketplace configurations

Corresponds to src/utils/plugins/marketplaceManager.ts
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import httpx

from .plugin_directories import (
    get_marketplaces_cache_dir,
    get_plugins_directory,
    get_versioned_cache_path,
)
from .plugin_identifier import parse_plugin_identifier
from .schemas import (
    KnownMarketplace,
    KnownMarketplacesFile,
    MarketplaceSource,
    PluginMarketplaceEntry,
    validate_marketplace_name,
)


# ============================================================================
# File Paths
# ============================================================================

def get_known_marketplaces_file() -> Path:
    """Get the known marketplaces configuration file path."""
    return get_plugins_directory() / 'known_marketplaces.json'


# ============================================================================
# Known Marketplaces Configuration
# ============================================================================

async def load_known_marketplaces_config() -> KnownMarketplacesFile:
    """Load known marketplaces configuration from disk.

    Returns:
        Configuration object mapping marketplace names to their metadata
    """
    fs = get_fs_implementation()
    config_file = get_known_marketplaces_file()

    try:
        content = await fs.read_file(config_file, encoding='utf-8')
        return json.loads(content)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse marketplace configuration: {e}")


async def save_known_marketplaces_config(config: KnownMarketplacesFile) -> None:
    """Save known marketplaces configuration to disk.

    Args:
        config: The marketplace configuration to save
    """
    fs = get_fs_implementation()
    config_file = get_known_marketplaces_file()

    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON string with proper formatting
    content = json.dumps(config, indent=2)
    await fs.write_file(config_file, content, encoding='utf-8')


# ============================================================================
# Marketplace Loading
# ============================================================================

async def get_marketplace(name: str) -> dict | None:
    """Get a marketplace by name (tries cache first, then fetches from source).

    Args:
        name: The marketplace name

    Returns:
        The marketplace data or None if not found
    """
    # Try cache first
    cached = await get_marketplace_cache_only(name)
    if cached:
        return cached

    # Cache miss - try fetching from source
    return await get_marketplace_from_source(name)


async def get_marketplace_cache_only(name: str) -> dict | None:
    """Get a marketplace from cache only (fast path).

    Args:
        name: The marketplace name

    Returns:
        The cached marketplace data or None if not in cache
    """
    config = await load_known_marketplaces_config()
    entry = config.get(name)

    if not entry:
        return None

    install_location = entry.get('installLocation')
    if not install_location:
        return None

    cache_path = Path(install_location)
    marketplace_file = cache_path / '.claude-plugin' / 'marketplace.json' if cache_path.is_dir() else cache_path

    if not marketplace_file.exists():
        return None

    try:
        with open(marketplace_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


async def get_marketplace_from_source(name: str) -> dict | None:
    """Fetch a marketplace from its source.

    Args:
        name: The marketplace name

    Returns:
        The marketplace data or None if not found
    """
    config = await load_known_marketplaces_config()
    entry = config.get(name)

    if not entry:
        return None

    source = entry.get('source', {})
    source_type = source.get('source')

    try:
        if source_type == 'url':
            return await fetch_marketplace_from_url(source['url'])
        elif source_type == 'github':
            return await fetch_marketplace_from_github(
                source['repo'],
                source.get('ref'),
            )
        elif source_type == 'git':
            return await fetch_marketplace_from_git(
                source['url'],
                source.get('ref'),
            )
        elif source_type == 'npm':
            return await fetch_marketplace_from_npm(source['package'])
        elif source_type == 'directory':
            return load_marketplace_from_directory(source['path'])
        elif source_type == 'file':
            return load_marketplace_from_file(source['path'])
        else:
            return None
    except Exception:
        return None


async def fetch_marketplace_from_url(url: str) -> dict | None:
    """Fetch a marketplace from a URL.

    Args:
        url: The marketplace URL

    Returns:
        The marketplace data or None if fetch failed
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except Exception:
        return None


async def fetch_marketplace_from_github(repo: str, ref: str | None = None) -> dict | None:
    """Fetch a marketplace from a GitHub repository.

    Args:
        repo: The GitHub repo (owner/repo)
        ref: The branch or tag ref

    Returns:
        The marketplace data or None if fetch failed
    """
    # Determine the API URL and file path
    parts = repo.split('/')
    if len(parts) != 2:
        return None

    owner, repo_name = parts
    ref = ref or 'main'

    # Try to fetch .claude-plugin/marketplace.json
    url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{ref}/.claude-plugin/marketplace.json"

    return await fetch_marketplace_from_url(url)


async def fetch_marketplace_from_git(url: str, ref: str | None = None) -> dict | None:
    """Fetch a marketplace from a git URL.

    Args:
        url: The git URL
        ref: The branch or tag ref

    Returns:
        The marketplace data or None if fetch failed
    """
    # This would require git operations - simplified for now
    return None


async def fetch_marketplace_from_npm(package: str) -> dict | None:
    """Fetch a marketplace from an npm package.

    Args:
        package: The npm package name

    Returns:
        The marketplace data or None if fetch failed
    """
    try:
        url = f"https://registry.npmjs.org/{package}/latest"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            # Try to get marketplace.json from the package
            if 'dist' in data and '.claude-plugin/marketplace.json' in data.get('files', []):
                # This is simplified - real implementation would need to handle tarball
                pass
            return None
    except Exception:
        return None


def load_marketplace_from_directory(path: str) -> dict | None:
    """Load a marketplace from a local directory.

    Args:
        path: The directory path

    Returns:
        The marketplace data or None if not found
    """
    marketplace_file = Path(path) / '.claude-plugin' / 'marketplace.json'

    if not marketplace_file.exists():
        return None

    try:
        with open(marketplace_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def load_marketplace_from_file(path: str) -> dict | None:
    """Load a marketplace from a JSON file.

    Args:
        path: The file path

    Returns:
        The marketplace data or None if not found
    """
    marketplace_file = Path(path)

    if not marketplace_file.exists():
        return None

    try:
        with open(marketplace_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


# ============================================================================
# Plugin Lookup
# ============================================================================

async def get_plugin_by_id(plugin_id: str) -> dict | None:
    """Get a plugin by its full ID (name@marketplace).

    Args:
        plugin_id: The plugin ID

    Returns:
        The plugin entry and marketplace install location, or None if not found
    """
    # Try cache-only first
    cached = await get_plugin_by_id_cache_only(plugin_id)
    if cached:
        return cached

    # Cache miss - try fetching from source
    return await get_plugin_by_id_from_source(plugin_id)


async def get_plugin_by_id_cache_only(plugin_id: str) -> dict | None:
    """Get a plugin by ID from cache only.

    Args:
        plugin_id: The plugin ID

    Returns:
        The plugin entry and marketplace install location, or None
    """
    parsed = parse_plugin_identifier(plugin_id)
    if not parsed.name or not parsed.marketplace:
        return None

    config = await load_known_marketplaces_config()
    marketplace_config = config.get(parsed.marketplace)

    if not marketplace_config:
        return None

    marketplace = await get_marketplace_cache_only(parsed.marketplace)
    if not marketplace:
        return None

    for plugin in marketplace.get('plugins', []):
        if plugin.get('name') == parsed.name:
            return {
                'entry': plugin,
                'marketplaceInstallLocation': marketplace_config.get('installLocation', ''),
            }

    return None


async def get_plugin_by_id_from_source(plugin_id: str) -> dict | None:
    """Get a plugin by ID, fetching from source if needed.

    Args:
        plugin_id: The plugin ID

    Returns:
        The plugin entry and marketplace install location, or None
    """
    parsed = parse_plugin_identifier(plugin_id)
    if not parsed.name or not parsed.marketplace:
        return None

    config = await load_known_marketplaces_config()
    marketplace_config = config.get(parsed.marketplace)

    if not marketplace_config:
        return None

    marketplace = await get_marketplace(parsed.marketplace)
    if not marketplace:
        return None

    for plugin in marketplace.get('plugins', []):
        if plugin.get('name') == parsed.name:
            return {
                'entry': plugin,
                'marketplaceInstallLocation': marketplace_config.get('installLocation', ''),
            }

    return None


async def search_plugin_in_marketplaces(
    plugin_name: str,
) -> tuple[PluginMarketplaceEntry | None, str | None, str | None]:
    """Search for a plugin across all configured marketplaces.

    Args:
        plugin_name: The plugin name to search for

    Returns:
        Tuple of (plugin_entry, marketplace_name, install_location) or (None, None, None)
    """
    config = await load_known_marketplaces_config()

    for mkt_name, mkt_config in config.items():
        marketplace = await get_marketplace(mkt_name)
        if not marketplace:
            continue

        for plugin in marketplace.get('plugins', []):
            if plugin.get('name') == plugin_name:
                return plugin, mkt_name, mkt_config.get('installLocation', '')

    return None, None, None


# ============================================================================
# Marketplace Operations
# ============================================================================

async def add_marketplace_source(
    source: MarketplaceSource,
    on_progress: Callable[[str], None] | None = None,
) -> tuple[str, bool, MarketplaceSource]:
    """Add a new marketplace source.

    Args:
        source: The marketplace source configuration
        on_progress: Optional callback for progress messages

    Returns:
        Tuple of (marketplace_name, already_materialized, resolved_source)
    """
    # Determine source type and extract name
    source_type = source.get('source')

    if source_type == 'github':
        repo = source.get('repo', '')
        name = repo.split('/')[-1] if '/' in repo else repo
    elif source_type == 'git':
        url = source.get('url', '')
        name = url.split('/')[-1].replace('.git', '') if '/' in url else 'git-marketplace'
    elif source_type == 'url':
        from urllib.parse import urlparse
        parsed = urlparse(source.get('url', ''))
        name = parsed.netloc.replace('.', '_')
    elif source_type == 'npm':
        name = source.get('package', 'npm-marketplace')
    elif source_type == 'directory':
        name = Path(source.get('path', '')).name or 'directory-marketplace'
    elif source_type == 'file':
        name = Path(source.get('path', '')).stem or 'file-marketplace'
    else:
        name = 'unknown-marketplace'

    # Validate name
    valid, error = validate_marketplace_name(name)
    if not valid:
        raise ValueError(error)

    config = await load_known_marketplaces_config()

    # Check if already exists
    already_materialized = name in config

    # Determine install location
    marketplaces_dir = get_marketplaces_cache_dir()
    install_location = str(marketplaces_dir / name)

    # Materialize the marketplace
    resolved_source = await materialize_marketplace(
        source, name, install_location, on_progress
    )

    # Update config
    config[name] = {
        'source': resolved_source,
        'installLocation': install_location,
        'lastUpdated': datetime.utcnow().isoformat() + 'Z',
        'autoUpdate': True,
    }

    await save_known_marketplaces_config(config)

    return name, already_materialized, resolved_source


async def materialize_marketplace(
    source: MarketplaceSource,
    name: str,
    install_location: str,
    on_progress: Callable[[str], None] | None = None,
) -> MarketplaceSource:
    """Materialize a marketplace to local cache.

    Args:
        source: The marketplace source
        name: The marketplace name
        install_location: Where to install
        on_progress: Optional callback for progress messages

    Returns:
        The resolved source
    """
    source_type = source.get('source')
    install_path = Path(install_location)

    if source_type == 'github':
        repo = source.get('repo', '')
        ref = source.get('ref') or 'main'

        if on_progress:
            on_progress(f"Cloning {repo}...")

        # Clone the repository
        try:
            if install_path.exists():
                shutil.rmtree(install_path)

            # Use git to clone
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', '--branch', ref, f'https://github.com/{repo}.git', str(install_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise ValueError(f"Failed to clone: {result.stderr}")

            return {
                'source': 'github',
                'repo': repo,
                'ref': ref,
            }
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {e}")

    elif source_type == 'url':
        url = source.get('url', '')

        if on_progress:
            on_progress(f"Fetching {url}...")

        marketplace_data = await fetch_marketplace_from_url(url)
        if not marketplace_data:
            raise ValueError(f"Failed to fetch marketplace from {url}")

        install_path.mkdir(parents=True, exist_ok=True)

        # Save to install location
        plugin_dir = install_path / '.claude-plugin'
        plugin_dir.mkdir(parents=True, exist_ok=True)

        with open(plugin_dir / 'marketplace.json', 'w') as f:
            json.dump(marketplace_data, f, indent=2)

        return source

    elif source_type == 'directory':
        src_path = Path(source.get('path', ''))
        if not src_path.exists():
            raise ValueError(f"Directory does not exist: {src_path}")

        if on_progress:
            on_progress(f"Linking {src_path}...")

        # Create symlink or copy
        if install_path.exists():
            shutil.rmtree(install_path)

        if src_path.is_dir():
            shutil.copytree(src_path, install_path, symlinks=True)
        else:
            install_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, install_path)

        return source

    elif source_type == 'file':
        src_path = Path(source.get('path', ''))
        if not src_path.exists():
            raise ValueError(f"File does not exist: {src_path}")

        install_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, install_path)

        return source

    # For other source types, use as-is
    return source


async def remove_marketplace_source(name: str) -> None:
    """Remove a marketplace source.

    Args:
        name: The marketplace name
    """
    config = await load_known_marketplaces_config()

    if name not in config:
        raise ValueError(f"Marketplace '{name}' not found")

    # Remove from config
    del config[name]
    await save_known_marketplaces_config(config)

    # Optionally remove cached files (optional - could keep for offline)
    install_location = config.get(name, {}).get('installLocation')
    if install_location and Path(install_location).exists():
        # Don't remove by default - user might want to keep cache
        pass


async def refresh_marketplace(
    name: str,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    """Refresh a marketplace from its source.

    Args:
        name: The marketplace name
        on_progress: Optional callback for progress messages
    """
    config = await load_known_marketplaces_config()
    entry = config.get(name)

    if not entry:
        raise ValueError(
            f"Marketplace '{name}' not found. Available marketplaces: {', '.join(config.keys())}"
        )

    source = entry.get('source', {})
    install_location = entry.get('installLocation', '')

    if on_progress:
        on_progress(f"Refreshing {name}...")

    # Re-materialize the marketplace
    await materialize_marketplace(source, name, install_location, on_progress)

    # Update lastUpdated
    entry['lastUpdated'] = datetime.utcnow().isoformat() + 'Z'
    config[name] = entry
    await save_known_marketplaces_config(config)


async def refresh_all_marketplaces() -> None:
    """Refresh all configured marketplaces."""
    config = await load_known_marketplaces_config()

    for name in config:
        try:
            await refresh_marketplace(name)
        except Exception:
            # Continue with other marketplaces
            pass


# ============================================================================
# Simple FS Implementation (for compatibility)
# ============================================================================

def get_fs_implementation():
    """Get a simple file system implementation."""

    class SimpleFS:
        @staticmethod
        async def read_file(path: Path, encoding: str = 'utf-8') -> str:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()

        @staticmethod
        async def write_file(path: Path, content: str, encoding: str = 'utf-8') -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

    return SimpleFS()


__all__ = [
    'get_known_marketplaces_file',
    'load_known_marketplaces_config',
    'save_known_marketplaces_config',
    'get_marketplace',
    'get_marketplace_cache_only',
    'get_marketplace_from_source',
    'get_plugin_by_id',
    'get_plugin_by_id_cache_only',
    'get_plugin_by_id_from_source',
    'search_plugin_in_marketplaces',
    'add_marketplace_source',
    'remove_marketplace_source',
    'refresh_marketplace',
    'refresh_all_marketplaces',
]