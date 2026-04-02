"""
Generic process utilities.

Process management helpers.
"""

import os
import signal
import subprocess
from typing import Optional, List, Dict, Any


def kill_process_tree(pid: int) -> bool:
    """Kill process and all its children.

    Args:
        pid: Process ID

    Returns:
        True if successful
    """
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except Exception:
        return False


def get_process_children(pid: int) -> List[int]:
    """Get child process IDs.

    Args:
        pid: Parent process ID

    Returns:
        List of child PIDs
    """
    try:
        result = subprocess.run(
            ["pgrep", "-P", str(pid)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return [int(p.strip()) for p in result.stdout.strip().split("\n") if p.strip()]
    except Exception:
        pass
    return []


def is_process_running(pid: int) -> bool:
    """Check if process is running.

    Args:
        pid: Process ID

    Returns:
        True if running
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


__all__ = [
    "kill_process_tree",
    "get_process_children",
    "is_process_running",
]