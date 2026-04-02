"""
Session restore utilities.

Session state restoration.
"""

import os
import json
from typing import Optional, Dict, Any


def get_session_restore_path(session_id: str) -> str:
    """Get session restore file path.

    Args:
        session_id: Session ID

    Returns:
        Restore file path
    """
    config_dir = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    return os.path.join(config_dir, "sessions", f"{session_id}.json")


def save_session_state(
    session_id: str,
    state: Dict[str, Any],
) -> bool:
    """Save session state for restoration.

    Args:
        session_id: Session ID
        state: Session state

    Returns:
        True if successful
    """
    try:
        path = get_session_restore_path(session_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(state, f)
        return True
    except Exception:
        return False


def load_session_state(session_id: str) -> Optional[Dict[str, Any]]:
    """Load session state.

    Args:
        session_id: Session ID

    Returns:
        Session state or None
    """
    try:
        path = get_session_restore_path(session_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def delete_session_state(session_id: str) -> None:
    """Delete session state.

    Args:
        session_id: Session ID
    """
    try:
        path = get_session_restore_path(session_id)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


__all__ = [
    "get_session_restore_path",
    "save_session_state",
    "load_session_state",
    "delete_session_state",
]