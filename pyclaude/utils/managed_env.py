"""
Managed environment utilities.

Environment variable management.
"""

import os
from typing import Dict, Optional, Any


def get_managed_env_vars() -> Dict[str, str]:
    """Get managed environment variables.

    Returns:
        Dict of managed env vars
    """
    return {
        "CLAUDE_CODE": "1",
        "CLAUDE_CODE_SESSION_ID": os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
    }


def set_managed_env_var(key: str, value: str) -> None:
    """Set a managed environment variable.

    Args:
        key: Variable name
        value: Variable value
    """
    os.environ[key] = value


def get_managed_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a managed environment variable.

    Args:
        key: Variable name
        default: Default value

    Returns:
        Variable value or default
    """
    return os.environ.get(key, default)


__all__ = [
    "get_managed_env_vars",
    "set_managed_env_var",
    "get_managed_env_var",
]