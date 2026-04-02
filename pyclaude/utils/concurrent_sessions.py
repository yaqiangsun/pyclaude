"""
Concurrent sessions utilities.

Manages concurrent CLI sessions for `claude ps`.
"""

import os
import json
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Type definitions
SessionKind = str  # 'interactive' | 'bg' | 'daemon' | 'daemon-worker'
SessionStatus = str  # 'busy' | 'idle' | 'waiting'


@dataclass
class SessionInfo:
    """Session information."""
    pid: int
    session_id: str
    cwd: str
    started_at: float
    kind: SessionKind
    entrypoint: Optional[str] = None
    name: Optional[str] = None
    log_path: Optional[str] = None
    agent: Optional[str] = None
    messaging_socket_path: Optional[str] = None
    bridge_session_id: Optional[str] = None
    status: Optional[SessionStatus] = None
    waiting_for: Optional[str] = None
    updated_at: Optional[float] = None


def get_sessions_dir() -> str:
    """Get sessions directory path."""
    config_home = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return os.path.join(config_home, "sessions")


def _get_session_kind_from_env() -> Optional[SessionKind]:
    """Get session kind from environment variable."""
    # Check for BG_SESSIONS feature flag
    if os.environ.get("BG_SESSIONS") == "1":
        kind = os.environ.get("CLAUDE_CODE_SESSION_KIND")
        if kind in ("bg", "daemon", "daemon-worker"):
            return kind
    return None


def is_bg_session() -> bool:
    """Check if running in a background session."""
    return _get_session_kind_from_env() == "bg"


def _get_current_pid() -> int:
    """Get current process ID."""
    return os.getpid()


def _get_session_id() -> str:
    """Get current session ID (placeholder)."""
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")


def _get_cwd() -> str:
    """Get current working directory."""
    return os.getcwd()


async def register_session() -> bool:
    """Register this session for concurrent session tracking.

    Returns:
        True if registered, False if skipped
    """
    kind: SessionKind = _get_session_kind_from_env() or "interactive"
    dir_path = get_sessions_dir()
    pid_file = os.path.join(dir_path, f"{_get_current_pid()}.json")

    try:
        # Create sessions directory
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o700)

        session_data = {
            "pid": _get_current_pid(),
            "sessionId": _get_session_id(),
            "cwd": _get_cwd(),
            "startedAt": int(os.time.time() * 1000),
            "kind": kind,
            "entrypoint": os.environ.get("CLAUDE_CODE_ENTRYPOINT"),
        }

        # Add feature-specific fields
        if os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET"):
            session_data["messagingSocketPath"] = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")

        if os.environ.get("CLAUDE_CODE_SESSION_NAME"):
            session_data["name"] = os.environ.get("CLAUDE_CODE_SESSION_NAME")
            session_data["logPath"] = os.environ.get("CLAUDE_CODE_SESSION_LOG")
            session_data["agent"] = os.environ.get("CLAUDE_CODE_AGENT")

        with open(pid_file, "w") as f:
            json.dump(session_data, f)

        return True
    except Exception as e:
        return False


async def update_pid_file(patch: Dict[str, Any]) -> None:
    """Update PID file with patch data.

    Args:
        patch: Fields to update
    """
    pid_file = os.path.join(get_sessions_dir(), f"{_get_current_pid()}.json")
    try:
        with open(pid_file, "r") as f:
            data = json.load(f)

        data.update(patch)

        with open(pid_file, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


async def update_session_name(name: Optional[str]) -> None:
    """Update session name.

    Args:
        name: New session name
    """
    if not name:
        return
    await update_pid_file({"name": name})


async def update_session_bridge_id(bridge_session_id: Optional[str]) -> None:
    """Update session's bridge ID.

    Args:
        bridge_session_id: Bridge session ID
    """
    await update_pid_file({"bridgeSessionId": bridge_session_id})


async def update_session_activity(
    status: Optional[SessionStatus] = None,
    waiting_for: Optional[str] = None,
) -> None:
    """Update session activity state.

    Args:
        status: Session status
        waiting_for: What the session is waiting for
    """
    if not os.environ.get("BG_SESSIONS"):
        return
    patch = {"updatedAt": int(os.time.time() * 1000)}
    if status:
        patch["status"] = status
    if waiting_for:
        patch["waitingFor"] = waiting_for
    await update_pid_file(patch)


async def count_concurrent_sessions() -> int:
    """Count live concurrent CLI sessions.

    Returns:
        Number of active sessions
    """
    dir_path = get_sessions_dir()

    try:
        files = os.listdir(dir_path)
    except Exception:
        return 0

    count = 0
    for file in files:
        # Only match <pid>.json pattern
        if not file.endswith(".json"):
            continue

        try:
            pid = int(file[:-5])
        except ValueError:
            continue

        if pid == _get_current_pid():
            count += 1
            continue

        # Check if process is running
        try:
            if psutil.pid_exists(pid):
                count += 1
            else:
                # Stale file - could delete but skip for safety
                pass
        except Exception:
            pass

    return count


__all__ = [
    "SessionKind",
    "SessionStatus",
    "SessionInfo",
    "get_sessions_dir",
    "is_bg_session",
    "register_session",
    "update_session_name",
    "update_session_bridge_id",
    "update_session_activity",
    "count_concurrent_sessions",
]