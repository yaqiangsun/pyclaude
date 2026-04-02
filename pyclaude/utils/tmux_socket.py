"""
Tmux socket utilities.

Tmux socket management.
"""

import os
import subprocess
from typing import Optional, List


def is_tmux_running() -> bool:
    """Check if running in tmux.

    Returns:
        True if in tmux
    """
    return bool(os.environ.get("TMUX"))


def get_tmux_socket() -> Optional[str]:
    """Get tmux socket path.

    Returns:
        Socket path or None
    """
    return os.environ.get("TMUX")


def tmux_send_keys(session: str, keys: str) -> bool:
    """Send keys to tmux session.

    Args:
        session: Session name
        keys: Keys to send

    Returns:
        True if successful
    """
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", session, keys],
            capture_output=True,
        )
        return True
    except Exception:
        return False


def tmux_list_sessions() -> List[str]:
    """List tmux sessions.

    Returns:
        List of session names
    """
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
    except Exception:
        pass
    return []


__all__ = [
    "is_tmux_running",
    "get_tmux_socket",
    "tmux_send_keys",
    "tmux_list_sessions",
]