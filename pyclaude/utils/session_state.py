"""
Session state utilities.

Session state management.
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SessionState:
    """Session state data."""
    session_id: str
    cwd: str
    created_at: float
    data: Dict[str, Any] = field(default_factory=dict)


# In-memory session state
_session_state: Optional[SessionState] = None


def get_session_state() -> Optional[SessionState]:
    """Get current session state.

    Returns:
        Session state or None
    """
    return _session_state


def set_session_state(state: SessionState) -> None:
    """Set current session state.

    Args:
        state: Session state
    """
    global _session_state
    _session_state = state


def get_session_id() -> str:
    """Get current session ID.

    Returns:
        Session ID
    """
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")


def get_session_cwd() -> str:
    """Get session working directory.

    Returns:
        Current directory
    """
    return os.getcwd()


__all__ = [
    "SessionState",
    "get_session_state",
    "set_session_state",
    "get_session_id",
    "get_session_cwd",
]