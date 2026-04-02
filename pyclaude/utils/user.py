"""
User utilities.

User information and preferences.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path


def get_username() -> str:
    """Get current username.

    Returns:
        Username
    """
    return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))


def get_user_email() -> Optional[str]:
    """Get user email from git config.

    Returns:
        Email or None
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_user_full_name() -> Optional[str]:
    """Get user full name from git config.

    Returns:
        Full name or None
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_user_info() -> Dict[str, Any]:
    """Get all user info.

    Returns:
        User info dict
    """
    return {
        "username": get_username(),
        "email": get_user_email(),
        "full_name": get_user_full_name(),
    }


__all__ = [
    "get_username",
    "get_user_email",
    "get_user_full_name",
    "get_user_info",
]