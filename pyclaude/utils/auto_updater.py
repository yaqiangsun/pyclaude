"""
Auto-updater utilities.

Handles checking for and installing updates.
"""

import os
import subprocess
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


GCS_BUCKET_URL = "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases"


class InstallStatus(str, Enum):
    SUCCESS = "success"
    NO_PERMISSIONS = "no_permissions"
    INSTALL_FAILED = "install_failed"
    IN_PROGRESS = "in_progress"


@dataclass
class AutoUpdaterResult:
    """Result of auto-update operation."""
    version: Optional[str]
    status: InstallStatus
    notifications: Optional[list] = None


def is_env_truthy(env_var: Optional[str]) -> bool:
    """Check if environment variable is truthy."""
    if not env_var:
        return False
    return env_var.lower() in ("1", "true", "yes", "on")


async def check_global_install_permissions() -> Dict[str, Any]:
    """Check if user has permissions for global npm install."""
    return {
        "hasPermissions": False,
        "npmPrefix": None,
    }


async def get_latest_version(channel: str) -> Optional[str]:
    """Get the latest version from npm registry."""
    npm_tag = "stable" if channel == "stable" else "latest"
    # Placeholder - would run npm view
    return None


async def get_npm_dist_tags() -> Dict[str, Optional[str]]:
    """Get npm dist-tags (latest and stable versions)."""
    return {"latest": None, "stable": None}


async def install_global_package(specific_version: Optional[str] = None) -> InstallStatus:
    """Install the global package (claude-code)."""
    return InstallStatus.INSTALL_FAILED


def get_lock_file_path() -> str:
    """Get the path to the update lock file."""
    config_home = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    return os.path.join(config_home, ".update.lock")


__all__ = [
    "InstallStatus",
    "AutoUpdaterResult",
    "GCS_BUCKET_URL",
    "check_global_install_permissions",
    "get_latest_version",
    "get_npm_dist_tags",
    "install_global_package",
    "get_lock_file_path",
]