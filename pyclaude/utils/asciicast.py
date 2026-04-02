"""
Asciicast recording utilities.

Records terminal sessions in asciicast format for playback.
"""

import os
import json
import time
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field

# Mutable recording state
_recording_state: Dict[str, Any] = {
    "filePath": None,
    "timestamp": 0,
}

_recorder: Optional["AsciicastRecorder"] = None


def is_env_truthy(env_var: Optional[str]) -> bool:
    """Check if environment variable is truthy."""
    if not env_var:
        return False
    return env_var.lower() in ("1", "true", "yes", "on")


def sanitize_path(path: str) -> str:
    """Sanitize path for use in filenames."""
    # Replace problematic characters
    return path.replace("/", "_").replace("\\", "_")


def get_record_file_path() -> Optional[str]:
    """Get the asciicast recording file path.

    Returns:
        Path to recording file, or None if recording is disabled
    """
    if _recording_state["filePath"] is not None:
        return _recording_state["filePath"]

    if os.environ.get("USER_TYPE") != "ant":
        return None

    if not is_env_truthy(os.environ.get("CLAUDE_CODE_TERMINAL_RECORDING")):
        return None

    # Get session ID and cwd from bootstrap state (placeholder)
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "unknown")
    cwd = os.environ.get("CLAUDE_CODE_CWD", os.getcwd())

    # Record alongside the transcript
    config_home = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    projects_dir = os.path.join(config_home, "projects")
    project_dir = os.path.join(projects_dir, sanitize_path(cwd))

    _recording_state["timestamp"] = int(time.time() * 1000)
    _recording_state["filePath"] = os.path.join(
        project_dir,
        f"{session_id}-{_recording_state['timestamp']}.cast",
    )
    return _recording_state["filePath"]


def _reset_recording_state_for_testing() -> None:
    """Reset recording state for testing."""
    _recording_state["filePath"] = None
    _recording_state["timestamp"] = 0


def get_session_recording_paths() -> List[str]:
    """Find all .cast files for the current session.

    Returns:
        List of paths sorted by filename (chronological)
    """
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not session_id:
        return []

    config_home = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    projects_dir = os.path.join(config_home, "projects")
    cwd = os.environ.get("CLAUDE_CODE_CWD", os.getcwd())
    project_dir = os.path.join(projects_dir, sanitize_path(cwd))

    try:
        if not os.path.exists(project_dir):
            return []
        files = [
            f for f in os.listdir(project_dir)
            if f.startswith(session_id) and f.endswith(".cast")
        ]
        files.sort()
        return [os.path.join(project_dir, f) for f in files]
    except Exception:
        return []


async def rename_recording_for_session() -> None:
    """Rename the recording file to match the current session ID."""
    old_path = _recording_state["filePath"]
    if not old_path or _recording_state["timestamp"] == 0:
        return

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    config_home = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    projects_dir = os.path.join(config_home, "projects")
    cwd = os.environ.get("CLAUDE_CODE_CWD", os.getcwd())
    project_dir = os.path.join(projects_dir, sanitize_path(cwd))

    new_path = os.path.join(
        project_dir,
        f"{session_id}-{_recording_state['timestamp']}.cast",
    )

    if old_path == new_path:
        return

    # Flush pending writes before renaming
    if _recorder:
        await _recorder.flush()

    try:
        os.rename(old_path, new_path)
        _recording_state["filePath"] = new_path
    except Exception:
        pass


def get_terminal_size() -> Dict[str, int]:
    """Get terminal size."""
    try:
        import shutil
        size = shutil.get_terminal_size()
        return {"cols": size.columns, "rows": size.lines}
    except Exception:
        return {"cols": 80, "rows": 24}


@dataclass
class AsciicastRecorder:
    """Asciicast recorder implementation."""

    file_path: str
    write_fn: Callable[[str], None]
    flush_interval_ms: int = 500
    max_buffer_size: int = 50
    max_buffer_bytes: int = 10 * 1024 * 1024

    _pending_write: Any = None

    async def flush(self) -> None:
        """Flush pending writes to disk."""
        pass

    async def dispose(self) -> None:
        """Dispose of the recorder."""
        pass


def flush_asciicast_recorder() -> None:
    """Flush pending recording data to disk."""
    pass


def install_asciicast_recorder() -> Optional[AsciicastRecorder]:
    """Install the asciicast recorder.

    Returns:
        The recorder instance, or None if recording is disabled
    """
    file_path = get_record_file_path()
    if not file_path:
        return None

    terminal_size = get_terminal_size()
    start_time = time.time()

    # Write asciicast v2 header
    header = json.dumps({
        "version": 2,
        "width": terminal_size["cols"],
        "height": terminal_size["rows"],
        "timestamp": int(time.time()),
        "env": {
            "SHELL": os.environ.get("SHELL", ""),
            "TERM": os.environ.get("TERM", ""),
        },
    })

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(header + "\n")
    except Exception:
        pass

    # Create recorder (simplified)
    global _recorder
    _recorder = AsciicastRecorder(
        file_path=file_path,
        write_fn=lambda content: None,  # Placeholder
    )

    return _recorder


__all__ = [
    "get_record_file_path",
    "get_session_recording_paths",
    "rename_recording_for_session",
    "flush_asciicast_recorder",
    "install_asciicast_recorder",
    "AsciicastRecorder",
]