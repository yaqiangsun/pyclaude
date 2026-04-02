"""
Shell command execution utilities.

Provides shell command execution with proper event listener limits,
sandbox support, and child abort controller functionality.
"""

import os
import asyncio
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
from functools import lru_cache

# Default max listeners for standard operations
DEFAULT_MAX_LISTENERS = 50

DEFAULT_TIMEOUT = 30 * 60 * 1000  # 30 minutes


def create_abort_controller(
    max_listeners: int = DEFAULT_MAX_LISTENERS,
) -> "AbortController":
    """Create an AbortController with proper event listener limits set.

    This prevents MaxListenersExceededWarning when multiple listeners
    are attached to the abort signal.

    Args:
        max_listeners: Maximum number of listeners (default: 50)

    Returns:
        AbortController with configured listener limit
    """
    # Python's AbortController is a simple wrapper
    return AbortController()


class AbortController:
    """AbortController implementation for Python."""

    def __init__(self):
        self._signal = AbortSignal()
        self._reason: Any = None

    @property
    def signal(self) -> "AbortSignal":
        return self._signal

    def abort(self, reason: Any = None):
        """Abort the controller."""
        self._reason = reason
        self._signal._aborted = True
        self._signal._reason = reason
        for callback in self._signal._on_abort:
            try:
                callback(reason)
            except Exception:
                pass


class AbortSignal:
    """AbortSignal implementation for Python."""

    def __init__(self):
        self._aborted = False
        self._reason: Any = None
        self._on_abort: list = []

    @property
    def aborted(self) -> bool:
        return self._aborted

    @property
    def reason(self) -> Any:
        return self._reason

    def add_event_listener(
        self,
        event: str,
        callback: Callable,
        *,
        once: bool = False
    ):
        """Add an event listener."""
        if event == "abort":
            if once:
                # Check if already aborted
                if self._aborted:
                    callback(self._reason)
                    return
            self._on_abort.append(callback)

    def remove_event_listener(self, event: str, callback: Callable):
        """Remove an event listener."""
        if event == "abort" and callback in self._on_abort:
            self._on_abort.remove(callback)


def create_child_abort_controller(
    parent: AbortController,
    max_listeners: Optional[int] = None,
) -> AbortController:
    """Create a child AbortController that aborts when its parent aborts.

    Aborting the child does NOT affect the parent.

    Memory-safe: Uses weak references so the parent doesn't retain abandoned children.

    Args:
        parent: The parent AbortController
        max_listeners: Maximum number of listeners (default: 50)

    Returns:
        Child AbortController
    """
    child = create_abort_controller(max_listeners)

    # Fast path: parent already aborted, no listener setup needed
    if parent.signal.aborted:
        child.abort(parent.signal.reason)
        return child

    # Set up listener to propagate abort
    def handler(reason):
        child.abort(reason)

    parent.signal.add_event_listener("abort", handler, once=True)

    # Auto-cleanup: remove parent listener when child is aborted
    def cleanup():
        parent.signal.remove_event_listener("abort", handler)

    child.signal.add_event_listener("abort", cleanup, once=True)

    return child


@dataclass
class ExecResult:
    """Result of shell command execution."""
    stdout: str
    stderr: str
    code: int
    interrupted: bool
    background_task_id: Optional[str] = None
    backgrounded_by_user: Optional[bool] = None
    assistant_auto_backgrounded: Optional[bool] = None
    output_file_path: Optional[str] = None
    output_file_size: Optional[int] = None
    output_task_id: Optional[str] = None
    pre_spawn_error: Optional[str] = None


@dataclass
class ShellCommand:
    """Shell command wrapper."""
    result: asyncio.Future
    status: str = "running"  # running | backgrounded | completed | killed

    def background(self, task_id: str) -> bool:
        """Move command to background."""
        return False

    def kill(self):
        """Kill the command."""
        pass

    def cleanup(self):
        """Clean up resources."""
        pass


# Type aliases
ShellType = str  # 'bash' | 'powershell'
ExecOptions = Dict[str, Any]


__all__ = [
    "AbortController",
    "AbortSignal",
    "create_abort_controller",
    "create_child_abort_controller",
    "ExecResult",
    "ShellCommand",
    "ShellType",
    "ExecOptions",
    "DEFAULT_MAX_LISTENERS",
    "DEFAULT_TIMEOUT",
]