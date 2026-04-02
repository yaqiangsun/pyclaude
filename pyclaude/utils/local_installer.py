"""
Local installer utilities.

Manages local installations.
"""

import os
import subprocess
from typing import Optional, Dict, Any


def get_installation_prefix() -> Optional[str]:
    """Get npm global installation prefix.

    Returns:
        Installation prefix path
    """
    try:
        result = subprocess.run(
            ["npm", "-g", "config", "get", "prefix"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def check_install_permissions() -> bool:
    """Check if user has install permissions.

    Returns:
        True if can install globally
    """
    prefix = get_installation_prefix()
    if not prefix:
        return False

    return os.access(prefix, os.W_OK)


def install_local_package(package: str) -> bool:
    """Install a package globally.

    Args:
        package: Package name

    Returns:
        True if successful
    """
    try:
        result = subprocess.run(
            ["npm", "install", "-g", package],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0
    except Exception:
        return False


def uninstall_local_package(package: str) -> bool:
    """Uninstall a global package.

    Args:
        package: Package name

    Returns:
        True if successful
    """
    try:
        result = subprocess.run(
            ["npm", "uninstall", "-g", package],
            capture_output=True,
            timeout=60,
        )
        return result.returncode == 0
    except Exception:
        return False


__all__ = [
    "get_installation_prefix",
    "check_install_permissions",
    "install_local_package",
    "uninstall_local_package",
]