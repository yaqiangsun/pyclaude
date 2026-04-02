"""
Repository detection utilities.

Parses git remote URLs and detects the current repository.
"""

import re
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass

# Cache for repository detection
_repository_cache: Dict[str, Optional["ParsedRepository"]] = {}


@dataclass
class ParsedRepository:
    """Parsed git repository information."""
    host: str
    owner: str
    name: str


def clear_repository_caches() -> None:
    """Clear the repository detection cache."""
    global _repository_cache
    _repository_cache.clear()


def _get_cwd() -> str:
    """Get current working directory."""
    import os
    return os.getcwd()


def _get_remote_url() -> Optional[str]:
    """Get git remote URL."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _looks_like_real_hostname(host: str) -> bool:
    """Check if hostname looks like a real domain name.

    Args:
        host: The hostname to check

    Returns:
        True if it looks like a real hostname
    """
    if "." not in host:
        return False
    last_segment = host.split(".")[-1]
    if not last_segment:
        return False
    # Real TLDs are purely alphabetic
    return bool(re.match(r"^[a-zA-Z]+$", last_segment))


def parse_git_remote(input_str: str) -> Optional[ParsedRepository]:
    """Parse a git remote URL into host, owner, and name.

    Supports:
      https://host/owner/repo.git
      git@host:owner/repo.git
      ssh://git@host/owner/repo.git
      git://host/owner/repo.git
      https://host/owner/repo (no .git)

    Args:
        input_str: The git remote URL to parse

    Returns:
        ParsedRepository or None if invalid
    """
    trimmed = input_str.strip()

    # SSH format: git@host:owner/repo.git
    ssh_match = re.match(r"^git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$", trimmed)
    if ssh_match and ssh_match.group(1) and ssh_match.group(2) and ssh_match.group(3):
        if not _looks_like_real_hostname(ssh_match.group(1)):
            return None
        return ParsedRepository(
            host=ssh_match.group(1),
            owner=ssh_match.group(2),
            name=ssh_match.group(3),
        )

    # URL format: https://host/owner/repo.git, ssh://git@host/owner/repo
    url_match = re.match(
        r"^(https?|ssh|git)://(?:[^@]+@)?([^/:]+(?::\d+)?)/([^/]+)/([^/]+?)(?:\.git)?$",
        trimmed,
    )
    if url_match and url_match.group(1) and url_match.group(2) and url_match.group(3) and url_match.group(4):
        protocol = url_match.group(1)
        host_with_port = url_match.group(2)
        host_without_port = host_with_port.split(":")[0] if ":" in host_with_port else host_with_port

        if not _looks_like_real_hostname(host_without_port):
            return None

        # Only preserve port for HTTPS
        host = host_with_port if protocol in ("https", "http") else host_without_port
        return ParsedRepository(
            host=host,
            owner=url_match.group(3),
            name=url_match.group(4),
        )

    return None


def parse_github_repository(input_str: str) -> Optional[str]:
    """Parse a git remote URL or "owner/repo" string and return "owner/repo".

    Only returns results for github.com hosts.

    Args:
        input_str: The input to parse

    Returns:
        "owner/repo" string or None
    """
    trimmed = input_str.strip()

    # Try parsing as a full remote URL
    parsed = parse_git_remote(trimmed)
    if parsed:
        if parsed.host != "github.com":
            return None
        return f"{parsed.owner}/{parsed.name}"

    # Check if it's already in owner/repo format
    if "://" not in trimmed and "@" not in trimmed and "/" in trimmed:
        parts = trimmed.split("/")
        if len(parts) == 2 and parts[0] and parts[1]:
            repo = parts[1].replace(".git", "")
            return f"{parts[0]}/{repo}"

    return None


async def detect_current_repository() -> Optional[str]:
    """Detect the current repository from git remote.

    Returns:
        "owner/repo" string or None (only for github.com)
    """
    result = await detect_current_repository_with_host()
    if not result:
        return None
    if result.host != "github.com":
        return None
    return f"{result.owner}/{result.name}"


async def detect_current_repository_with_host() -> Optional[ParsedRepository]:
    """Detect the current repository with host information.

    Returns:
        ParsedRepository or None
    """
    global _repository_cache
    cwd = _get_cwd()

    if cwd in _repository_cache:
        return _repository_cache.get(cwd)

    try:
        remote_url = _get_remote_url()
        if not remote_url:
            _repository_cache[cwd] = None
            return None

        parsed = parse_git_remote(remote_url)
        _repository_cache[cwd] = parsed
        return parsed
    except Exception:
        _repository_cache[cwd] = None
        return None


def get_cached_repository() -> Optional[str]:
    """Get cached github.com repository for current cwd.

    Returns:
        "owner/repo" string or None
    """
    cwd = _get_cwd()
    parsed = _repository_cache.get(cwd)
    if not parsed or parsed.host != "github.com":
        return None
    return f"{parsed.owner}/{parsed.name}"


__all__ = [
    "ParsedRepository",
    "clear_repository_caches",
    "parse_git_remote",
    "parse_github_repository",
    "detect_current_repository",
    "detect_current_repository_with_host",
    "get_cached_repository",
]