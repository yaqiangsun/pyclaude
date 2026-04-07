"""Plugin loader and cache management.

Provides functions for caching plugins and loading plugin manifests.
Corresponds to src/utils/plugins/pluginLoader.ts
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


# ============================================================================
# Plugin Caching
# ============================================================================

async def cache_plugin(
    source: str | dict | None,
    options: dict | None = None,
) -> dict:
    """Cache a plugin to local disk.

    Args:
        source: Plugin source (string path, or dict with source type)
        options: Optional configuration

    Returns:
        Dict with path, manifest, and optional git_commit_sha
    """
    options = options or {}
    manifest = options.get('manifest', {})
    source_path = options.get('source_path')

    from .plugin_directories import get_plugin_cache_dir

    cache_dir = get_plugin_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Handle local source (string path)
    if isinstance(source, str):
        src = Path(source)
        if src.exists():
            # Copy to temp location then to cache
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir) / 'plugin'
                if src.is_dir():
                    shutil.copytree(src, tmp_path, symlinks=True)
                else:
                    shutil.copy2(src, tmp_path)

                return {
                    'path': str(tmp_path),
                    'manifest': manifest,
                    'git_commit_sha': await get_git_commit_sha(str(src)),
                }

    # Handle dict source (github, npm, etc.)
    if isinstance(source, dict):
        source_type = source.get('source')

        if source_type == 'github':
            return await cache_plugin_from_github(source, manifest)
        elif source_type == 'git':
            return await cache_plugin_from_git(source, manifest)
        elif source_type == 'npm':
            return await cache_plugin_from_npm(source, manifest)

    # No source or unknown - return empty cache entry
    return {
        'path': '',
        'manifest': manifest,
        'git_commit_sha': None,
    }


async def cache_plugin_from_github(source: dict, manifest: dict) -> dict:
    """Cache a plugin from GitHub.

    Args:
        source: GitHub source config
        manifest: Plugin manifest

    Returns:
        Dict with path and metadata
    """
    repo = source.get('repo', '')
    ref = source.get('ref', 'main')
    subdir = source.get('subdir')

    from .plugin_directories import get_plugin_cache_dir

    # Create unique cache key from repo and ref
    cache_key = hashlib.sha256(f"{repo}:{ref}".encode()).hexdigest()[:16]
    cache_path = get_plugin_cache_dir() / 'temp' / cache_key

    try:
        # Clone the repository
        if cache_path.exists():
            shutil.rmtree(cache_path)

        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--branch', ref, f'https://github.com/{repo}.git', str(cache_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise ValueError(f"Git clone failed: {result.stderr}")

        git_sha = await get_git_commit_sha(str(cache_path))

        # If subdir specified, use that
        if subdir:
            final_path = cache_path / subdir
            if not final_path.exists():
                raise ValueError(f"Subdir '{subdir}' not found in repository")
        else:
            final_path = cache_path

        return {
            'path': str(final_path),
            'manifest': manifest,
            'git_commit_sha': git_sha,
        }

    except subprocess.TimeoutExpired:
        raise ValueError("Git clone timed out")
    except Exception as e:
        raise ValueError(f"Failed to cache plugin from GitHub: {e}")


async def cache_plugin_from_git(source: dict, manifest: dict) -> dict:
    """Cache a plugin from a git URL.

    Args:
        source: Git source config
        manifest: Plugin manifest

    Returns:
        Dict with path and metadata
    """
    url = source.get('url', '')
    ref = source.get('ref', 'main')
    subdir = source.get('subdir')

    from .plugin_directories import get_plugin_cache_dir

    cache_key = hashlib.sha256(f"{url}:{ref}".encode()).hexdigest()[:16]
    cache_path = get_plugin_cache_dir() / 'temp' / cache_key

    try:
        if cache_path.exists():
            shutil.rmtree(cache_path)

        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--branch', ref, url, str(cache_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise ValueError(f"Git clone failed: {result.stderr}")

        git_sha = await get_git_commit_sha(str(cache_path))

        if subdir:
            final_path = cache_path / subdir
            if not final_path.exists():
                raise ValueError(f"Subdir '{subdir}' not found in repository")
        else:
            final_path = cache_path

        return {
            'path': str(final_path),
            'manifest': manifest,
            'git_commit_sha': git_sha,
        }

    except Exception as e:
        raise ValueError(f"Failed to cache plugin from git: {e}")


async def cache_plugin_from_npm(source: dict, manifest: dict) -> dict:
    """Cache a plugin from npm.

    Args:
        source: NPM source config
        manifest: Plugin manifest

    Returns:
        Dict with path and metadata
    """
    import httpx
    import tarfile
    import io

    package = source.get('package', '')

    try:
        # Get package info
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://registry.npmjs.org/{package}/latest", timeout=30.0)
            response.raise_for_status()
            pkg_info = response.json()

        # Get tarball URL
        tarball_url = pkg_info.get('dist', {}).get('tarball')
        if not tarball_url:
            raise ValueError("No tarball URL found in package")

        # Download tarball
        async with httpx.AsyncClient() as client:
            response = await client.get(tarball_url, timeout=60.0)
            response.raise_for_status()

        # Extract to cache
        from .plugin_directories import get_plugin_cache_dir

        cache_key = hashlib.sha256(package.encode()).hexdigest()[:16]
        cache_path = get_plugin_cache_dir() / 'temp' / cache_key
        cache_path.mkdir(parents=True, exist_ok=True)

        # Extract tarball
        with tarfile.open(fileobj=io.BytesIO(response.content)) as tar:
            # Extract only the package directory
            for member in tar.getmembers():
                # Package contents are in package/ or name-version/
                if '/' in member.name:
                    member.name = '/'.join(member.name.split('/')[1:])
                    if member.name:
                        tar.extract(member, cache_path)

        return {
            'path': str(cache_path),
            'manifest': manifest,
            'git_commit_sha': None,
        }

    except Exception as e:
        raise ValueError(f"Failed to cache plugin from npm: {e}")


async def get_git_commit_sha(path: str) -> str | None:
    """Get the current Git commit SHA for a path.

    Args:
        path: The path to check

    Returns:
        The commit SHA or None if not a git repo
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


# ============================================================================
# Version Calculation
# ============================================================================

async def calculate_plugin_version(
    plugin_id: str,
    source: str | dict | None,
    fallback_version: str | None,
    source_path: str = '',
) -> str:
    """Calculate the version for a plugin.

    Args:
        plugin_id: The plugin ID
        source: The plugin source
        fallback_version: Fallback version from marketplace
        source_path: Path to the plugin source

    Returns:
        The calculated version string
    """
    # Try to get version from manifest
    if source_path:
        manifest_path = Path(source_path) / '.claude-plugin' / 'plugin.json'
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    if manifest.get('version'):
                        return manifest['version']
            except (json.JSONDecodeError, IOError):
                pass

    # Try git SHA if it's a git repo
    if source_path:
        sha = await get_git_commit_sha(source_path)
        if sha:
            return sha[:8]

    # Use fallback version or generate one
    if fallback_version:
        return fallback_version

    # Generate a hash-based version
    if source:
        if isinstance(source, dict):
            key = json.dumps(source, sort_keys=True)
        else:
            key = str(source)
        return hashlib.sha256(key.encode()).hexdigest()[:8]

    return '0.0.0'


# ============================================================================
# Manifest Loading
# ============================================================================

async def load_plugin_manifest(path: str, name: str, source: str | None = None) -> dict | None:
    """Load a plugin manifest from disk.

    Args:
        path: Path to the plugin
        name: Plugin name
        source: Source string (for logging)

    Returns:
        The plugin manifest or None if not found
    """
    plugin_dir = Path(path)

    # Look for .claude-plugin/plugin.json
    manifest_paths = [
        plugin_dir / '.claude-plugin' / 'plugin.json',
        plugin_dir / 'plugin.json',
    ]

    for manifest_path in manifest_paths:
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None

    return None


__all__ = [
    'cache_plugin',
    'cache_plugin_from_github',
    'cache_plugin_from_git',
    'cache_plugin_from_npm',
    'get_git_commit_sha',
    'calculate_plugin_version',
    'load_plugin_manifest',
]