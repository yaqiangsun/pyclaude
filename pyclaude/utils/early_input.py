"""
Early Input Capture

This module captures terminal input that is typed before the REPL is fully
initialized. Users often type `claude` and immediately start typing their
prompt, but those early keystrokes would otherwise be lost during startup.

Usage:
1. Call start_capturing_early_input() as early as possible
2. When REPL is ready, call consume_early_input() to get any buffered text
3. stop_capturing_early_input() is called automatically when input is consumed
"""

import sys
import os
from typing import Optional

# Buffer for early input characters
_early_input_buffer = ""
# Flag to track if we're currently capturing
_is_capturing = False


def start_capturing_early_input() -> bool:
    """Start capturing stdin data early, before the REPL is initialized.

    Should be called as early as possible in the startup sequence.

    Only captures if stdin is a TTY (interactive terminal).

    Returns:
        True if capture started successfully
    """
    global _early_input_buffer, _is_capturing

    # Only capture in interactive mode
    if (
        not sys.stdin.isatty() or
        _is_capturing or
        "-p" in sys.argv or
        "--print" in sys.argv
    ):
        return False

    _is_capturing = True
    _early_input_buffer = ""

    return True


def _process_chunk_chunk(str_data: str) -> None:
    """Process a chunk of input data."""
    global _early_input_buffer

    i = 0
    while i < len(str_data):
        char = str_data[i]
        code = ord(char)

        # Ctrl+C (code 3) - stop capturing and exit
        if code == 3:
            stop_capturing_early_input()
            sys.exit(130)

        # Ctrl+D (code 4) - EOF, stop capturing
        if code == 4:
            stop_capturing_early_input()
            return

        # Backspace (code 127 or 8) - remove last character
        if code == 127 or code == 8:
            if len(_early_input_buffer) > 0:
                _early_input_buffer = _early_input_buffer[:-1]
            i += 1
            continue

        # Skip escape sequences (arrow keys, function keys, etc.)
        if code == 27:
            i += 1
            while (
                i < len(str_data) and
                not (64 <= ord(str_data[i]) <= 126)
            ):
                i += 1
            if i < len(str_data):
                i += 1
            continue

        # Skip other control characters (except tab and newline)
        if code < 32 and code != 9 and code != 10 and code != 13:
            i += 1
            continue

        # Convert carriage return to newline
        if code == 13:
            _early_input_buffer += "\n"
            i += 1
            continue

        # Add printable characters to buffer
        _early_input_buffer += char
        i += 1


def stop_capturing_early_input() -> None:
    """Stop capturing early input."""
    global _is_capturing

    if not _is_capturing:
        return

    _is_capturing = False


def consume_early_input() -> str:
    """Consume any early input that was captured.

    Returns the captured input and clears the buffer.
    Automatically stops capturing when called.

    Returns:
        The captured early input
    """
    global _early_input_buffer

    stop_capturing_early_input()
    input_text = _early_input_buffer.strip()
    _early_input_buffer = ""
    return input_text


def has_early_input() -> bool:
    """Check if there is any early input available without consuming it.

    Returns:
        True if early input is available
    """
    return len(_early_input_buffer.strip()) > 0


def seed_early_input(text: str) -> None:
    """Seed the early input buffer with text.

    Args:
        text: Text to seed
    """
    global _early_input_buffer
    _early_input_buffer = text


def is_capturing_early_input() -> bool:
    """Check if early input capture is currently active.

    Returns:
        True if capturing
    """
    return _is_capturing


__all__ = [
    "start_capturing_early_input",
    "stop_capturing_early_input",
    "consume_early_input",
    "has_early_input",
    "seed_early_input",
    "is_capturing_early_input",
]