"""
Ink hooks - React hooks adaptation for Python terminal UI.
"""
import asyncio
import os
import sys
import signal
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class StdinState(Enum):
    """Stdin state."""
    IDLE = "idle"
    READY = "ready"
    ACTIVE = "active"


@dataclass
class KeyboardEvent:
    """Keyboard event."""
    key: str
    alt: bool = False
    ctrl: bool = False
    shift: bool = False
    meta: bool = False


@dataclass
class TerminalSize:
    """Terminal size."""
    width: int
    height: int


# Global stdin state
_stdin_state = StdinState.IDLE
_input_callback: Optional[Callable] = None
_terminal_size = TerminalSize(width=80, height=24)


def get_stdin_state() -> StdinState:
    """Get current stdin state."""
    return _stdin_state


def set_stdin_state(state: StdinState) -> None:
    """Set stdin state."""
    global _stdin_state
    _stdin_state = state


def get_terminal_size() -> TerminalSize:
    """Get current terminal size."""
    return _terminal_size


def update_terminal_size(width: int, height: int) -> None:
    """Update terminal size."""
    global _terminal_size
    _terminal_size = TerminalSize(width=width, height=height)


# Animation frame handling
_animation_frame_callbacks: List[Callable] = []
_animation_running = False


def use_animation_frame(callback: Callable[[float], None]) -> None:
    """
    Hook for animation frames.
    Similar to requestAnimationFrame in React.
    """
    _animation_frame_callbacks.append(callback)


def start_animation_loop() -> None:
    """Start the animation loop."""
    global _animation_running
    if _animation_running:
        return

    _animation_running = True
    _run_animation_loop()


def _run_animation_loop() -> None:
    """Run the animation loop."""
    if not _animation_running:
        return

    # Simple time-based callback
    import time
    current_time = time.time()

    for callback in _animation_frame_callbacks:
        try:
            callback(current_time)
        except Exception:
            pass

    # Schedule next frame (roughly 60fps)
    loop = asyncio.get_event_loop()
    loop.call_later(1/60, _run_animation_loop)


def stop_animation_loop() -> None:
    """Stop the animation loop."""
    global _animation_running
    _animation_running = False


# Interval hook
_interval_handles: Dict[str, asyncio.Task] = {}


def use_interval(callback: Callable, delay_ms: int) -> str:
    """
    Hook for setInterval-like behavior.
    Returns an interval handle.
    """
    import uuid
    handle = str(uuid.uuid4())

    async def run_interval():
        while handle in _interval_handles:
            try:
                callback()
            except Exception:
                pass
            await asyncio.sleep(delay_ms / 1000)

    loop = asyncio.get_event_loop()
    task = loop.create_task(run_interval())
    _interval_handles[handle] = task
    return handle


def clear_interval(handle: str) -> None:
    """Clear an interval."""
    if handle in _interval_handles:
        _interval_handles[handle].cancel()
        del _interval_handles[handle]


# Terminal focus tracking
_focused = True


def use_terminal_focus() -> bool:
    """Hook to track terminal focus."""
    return _focused


def set_terminal_focus(focused: bool) -> None:
    """Set terminal focus state."""
    global _focused
    _focused = focused


# Terminal title
_terminal_title = ""


def use_terminal_title() -> str:
    """Hook to get/set terminal title."""
    return _terminal_title


def set_terminal_title(title: str) -> None:
    """Set terminal title."""
    global _terminal_title
    _terminal_title = title

    # Set actual terminal title
    if sys.platform != 'win32':
        sys.stdout.write(f"\x1b]2;{title}\x1b\\")
        sys.stdout.flush()


# Terminal viewport
_viewport_start = 0
_viewport_height = 24


def use_terminal_viewport() -> tuple:
    """Hook to get terminal viewport."""
    return (_viewport_start, _viewport_height)


def set_viewport(start: int, height: int) -> None:
    """Set viewport parameters."""
    global _viewport_start, _viewport_height
    _viewport_start = start
    _viewport_height = height


# Input handling
def use_input(
    input_callback: Callable[[str, KeyboardEvent], None],
    is_active: bool = True,
) -> None:
    """
    Hook for handling user input.
    """
    global _input_callback
    if is_active:
        _input_callback = input_callback
        set_stdin_state(StdinState.ACTIVE)
    else:
        _input_callback = None
        set_stdin_state(StdinState.IDLE)


def process_input(key: str, event: KeyboardEvent) -> None:
    """Process input through the callback."""
    if _input_callback:
        try:
            _input_callback(key, event)
        except Exception:
            pass


# Tab status
_tab_count = 0


def use_tab_status() -> int:
    """Hook to get the current tab count."""
    return _tab_count


def increment_tab_count() -> None:
    """Increment the tab count."""
    global _tab_count
    _tab_count += 1


def reset_tab_count() -> None:
    """Reset tab count to 0."""
    global _tab_count
    _tab_count = 0


# Selection (for text selection in terminal)
_selection_start: Optional[tuple] = None
_selection_end: Optional[tuple] = None


def use_selection() -> tuple:
    """Hook to get current selection."""
    return (_selection_start, _selection_end)


def set_selection(start: Optional[tuple], end: Optional[tuple]) -> None:
    """Set selection range."""
    global _selection_start, _selection_end
    _selection_start = start
    _selection_end = end


def clear_selection() -> None:
    """Clear selection."""
    global _selection_start, _selection_end
    _selection_start = None
    _selection_end = None


# Search highlight
_search_query = ""
_search_matches: List[tuple] = []


def use_search_highlight() -> tuple:
    """Hook for search highlight."""
    return (_search_query, _search_matches)


def set_search_query(query: str, matches: List[tuple]) -> None:
    """Set search query and matches."""
    global _search_query, _search_matches
    _search_query = query
    _search_matches = matches


def clear_search() -> None:
    """Clear search."""
    global _search_query, _search_matches
    _search_query = ""
    _search_matches = []


__all__ = [
    'StdinState',
    'KeyboardEvent',
    'TerminalSize',
    'get_stdin_state',
    'set_stdin_state',
    'get_terminal_size',
    'update_terminal_size',
    'use_animation_frame',
    'start_animation_loop',
    'stop_animation_loop',
    'use_interval',
    'clear_interval',
    'use_terminal_focus',
    'set_terminal_focus',
    'use_terminal_title',
    'set_terminal_title',
    'use_terminal_viewport',
    'set_viewport',
    'use_input',
    'process_input',
    'use_tab_status',
    'increment_tab_count',
    'reset_tab_count',
    'use_selection',
    'set_selection',
    'clear_selection',
    'use_search_highlight',
    'set_search_query',
    'clear_search',
]