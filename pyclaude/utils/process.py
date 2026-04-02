"""
Process utilities.

Process management and information.
"""

import os
import sys
from typing import Optional, Dict, Any


def get_pid() -> int:
    """Get current process ID.

    Returns:
        Process ID
    """
    return os.getpid()


def get_parent_pid() -> int:
    """Get parent process ID.

    Returns:
        Parent process ID
    """
    return os.getppid()


def get_process_info() -> Dict[str, Any]:
    """Get current process information.

    Returns:
        Process info dict
    """
    return {
        "pid": get_pid(),
        "ppid": get_parent_pid(),
        "platform": sys.platform,
        "python_version": sys.version,
    }


def is_main_process() -> bool:
    """Check if this is the main process.

    Returns:
        True if main process
    """
    return True  # Simplified


def get_environment() -> Dict[str, str]:
    """Get process environment variables.

    Returns:
        Environment dict
    """
    return dict(os.environ)


__all__ = [
    "get_pid",
    "get_parent_pid",
    "get_process_info",
    "is_main_process",
    "get_environment",
]