"""
Use double press hook.

Creates a function that calls one function on the first call and another
function on the second call within a certain timeout.
"""

import time
from typing import Callable, Optional

DOUBLE_PRESS_TIMEOUT_MS = 800


class DoublePressHandler:
    """Handler for double press detection."""

    def __init__(
        self,
        set_pending: Callable[[bool], None],
        on_double_press: Callable[[], None],
        on_first_press: Optional[Callable[[], None]] = None,
    ):
        self._set_pending = set_pending
        self._on_double_press = on_double_press
        self._on_first_press = on_first_press
        self._last_press_time = 0
        self._timeout_handle = None
        self._pending = False

    def _clear_timeout(self) -> None:
        """Clear the timeout safely."""
        if self._timeout_handle:
            try:
                self._timeout_handle.cancel()
            except Exception:
                pass
            self._timeout_handle = None

    def __call__(self) -> None:
        """Handle press event."""
        now = int(time.time() * 1000)
        time_since_last_press = now - self._last_press_time
        is_double_press = (
            time_since_last_press <= DOUBLE_PRESS_TIMEOUT_MS and
            self._pending
        )

        if is_double_press:
            # Double press detected
            self._clear_timeout()
            self._pending = False
            self._set_pending(False)
            self._on_double_press()
        else:
            # First press
            if self._on_first_press:
                self._on_first_press()
            self._pending = True
            self._set_pending(True)

            # Clear any existing timeout and set new one
            self._clear_timeout()

            def timeout_callback():
                self._pending = False
                self._set_pending(False)
                self._timeout_handle = None

            self._timeout_handle = threading.Timer(
                DOUBLE_PRESS_TIMEOUT_MS / 1000.0,
                timeout_callback
            )
            self._timeout_handle.start()

        self._last_press_time = now

    def cleanup(self) -> None:
        """Clean up timeout on cleanup."""
        self._clear_timeout()


# Need threading
import threading


def use_double_press(
    set_pending: Callable[[bool], None],
    on_double_press: Callable[[], None],
    on_first_press: Optional[Callable[[], None]] = None,
) -> DoublePressHandler:
    """Create a double press handler.

    Args:
        set_pending: Callback to set pending state
        on_double_press: Callback for double press
        on_first_press: Optional callback for first press

    Returns:
        DoublePressHandler that can be called on press events
    """
    return DoublePressHandler(set_pending, on_double_press, on_first_press)


__all__ = ["DOUBLE_PRESS_TIMEOUT_MS", "DoublePressHandler", "use_double_press"]