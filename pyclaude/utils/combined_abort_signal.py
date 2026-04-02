"""
Combined abort signal utilities.

Creates a combined AbortSignal that aborts when the input signal aborts,
an optional second signal aborts, or an optional timeout elapses.
"""

import signal
from typing import Any, Callable, Optional, Tuple


class AbortSignal:
    """Minimal AbortSignal implementation."""

    def __init__(self):
        self._aborted = False
        self._abort_reason: Optional[Any] = None
        self._listeners: list = []

    @property
    def aborted(self) -> bool:
        return self._aborted

    def abort(self, reason: Any = None) -> None:
        self._aborted = True
        self._abort_reason = reason
        for listener in self._listeners:
            listener(reason)

    def add_event_listener(self, event: str, callback: Callable) -> None:
        if event == "abort":
            self._listeners.append(callback)

    def remove_event_listener(self, event: str, callback: Callable) -> None:
        if event == "abort" and callback in self._listeners:
            self._listeners.remove(callback)


class AbortController:
    """Minimal AbortController implementation."""

    def __init__(self):
        self.signal = AbortSignal()

    def abort(self, reason: Any = None) -> None:
        self.signal.abort(reason)


def create_abort_controller() -> AbortController:
    """Create an AbortController.

    Returns:
        AbortController instance
    """
    return AbortController()


def create_combined_abort_signal(
    sig: Optional[signal.Signals],
    opts: Optional[dict] = None,
) -> Tuple[signal.Signals, Callable[[], None]]:
    """Create a combined abort signal.

    Args:
        sig: Original signal to listen to
        opts: Optional dict with signalB and timeout_ms

    Returns:
        Tuple of (signal, cleanup function)
    """
    signal_b = opts.get("signal_b") if opts else None
    timeout_ms = opts.get("timeout_ms") if opts else None

    combined = create_abort_controller()
    cleanup_funcs = []

    def abort_combined():
        combined.abort()

    if sig is not None and sig != signal.SIGABRT:
        # Handle timeout if specified
        timer = None
        if timeout_ms is not None:
            def timeout_handler():
                abort_combined()
            timer = signal.signal(sig, timeout_handler)
            cleanup_funcs.append(lambda: signal.signal(sig, signal.SIG_DFL))

    if timeout_ms is not None:
        import threading
        timer = threading.Timer(timeout_ms / 1000.0, abort_combined)
        timer.daemon = True
        timer.start()
        cleanup_funcs.append(timer.cancel)

    def cleanup():
        for func in cleanup_funcs:
            func()

    return combined.signal, cleanup


__all__ = [
    "AbortSignal",
    "AbortController",
    "create_abort_controller",
    "create_combined_abort_signal",
]