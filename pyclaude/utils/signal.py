"""
Signal utilities.

Signal handling helpers.
"""

import signal
import asyncio
from typing import Callable, Optional, Set


class SignalHandler:
    """Handle OS signals."""

    def __init__(self):
        self._handlers: dict = {}
        self._original_handlers: dict = {}

    def register(self, sig: int, handler: Callable) -> None:
        """Register signal handler.

        Args:
            sig: Signal number
            handler: Handler function
        """
        self._original_handlers[sig] = signal.signal(sig, handler)
        self._handlers[sig] = handler

    def unregister(self, sig: int) -> None:
        """Unregister signal handler.

        Args:
            sig: Signal number
        """
        if sig in self._original_handlers:
            signal.signal(sig, self._original_handlers[sig])
            del self._handlers[sig]


def create_signal_handler() -> SignalHandler:
    """Create signal handler.

    Returns:
        Signal handler
    """
    return SignalHandler()


def handle_signals(handlers: dict) -> None:
    """Handle common signals.

    Args:
        handlers: Dict of signal -> handler
    """
    for sig, handler in handlers.items():
        signal.signal(sig, handler)


__all__ = [
    "SignalHandler",
    "create_signal_handler",
    "handle_signals",
]