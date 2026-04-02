"""
Unary logging utilities.

Single-line logging updates.
"""

import sys
from typing import Optional
import time


class UnaryLogger:
    """Single-line logger that updates in place."""

    def __init__(self, stream=None):
        self.stream = stream or sys.stderr
        self.last_len = 0

    def write(self, message: str) -> None:
        """Write message, overwriting previous line.

        Args:
            message: Message to write
        """
        # Clear previous line
        if self.last_len > 0:
            self.stream.write("\r" + " " * self.last_len + "\r")

        self.stream.write(message)
        self.stream.flush()
        self.last_len = len(message)

    def clear(self) -> None:
        """Clear the current line."""
        if self.last_len > 0:
            self.stream.write("\r" + " " * self.last_len + "\r")
            self.stream.flush()
            self.last_len = 0


# Global unary logger
_unary_logger = UnaryLogger()


def get_unary_logger() -> UnaryLogger:
    """Get global unary logger."""
    return _unary_logger


__all__ = [
    "UnaryLogger",
    "get_unary_logger",
]