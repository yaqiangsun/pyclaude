"""
Ink output - Output handling for terminal rendering.
"""
import sys
import os
from typing import Optional, List
from io import StringIO


class Output:
    """Handles output to terminal."""

    def __init__(self, write_stream: Optional[any] = None):
        self._stream = write_stream or sys.stdout
        self._buffer = StringIO()
        self._columns: Optional[int] = None
        self._rows: Optional[int] = None

    def write(self, text: str) -> None:
        """Write text to output."""
        self._stream.write(text)
        self._stream.flush()

    def write_raw(self, text: str) -> None:
        """Write raw text without buffering."""
        self._stream.write(text)
        self._stream.flush()

    def clear_screen(self) -> None:
        """Clear the entire screen."""
        self.write_raw('\x1b[2J\x1b[H')

    def clear_line(self) -> None:
        """Clear the current line."""
        self.write_raw('\x1b[2K')

    def move_cursor(self, x: int, y: int) -> None:
        """Move cursor to position."""
        self.write_raw(f'\x1b[{y};{x}H')

    def move_cursor_up(self, lines: int = 1) -> None:
        """Move cursor up."""
        self.write_raw(f'\x1b[{lines}A')

    def move_cursor_down(self, lines: int = 1) -> None:
        """Move cursor down."""
        self.write_raw(f'\x1b[{lines}B')

    def move_cursor_forward(self, cols: int = 1) -> None:
        """Move cursor forward."""
        self.write_raw(f'\x1b[{cols}C')

    def move_cursor_back(self, cols: int = 1) -> None:
        """Move cursor back."""
        self.write_raw(f'\x1b[{cols}D')

    def save_cursor_position(self) -> None:
        """Save cursor position."""
        self.write_raw('\x1b7')

    def restore_cursor_position(self) -> None:
        """Restore cursor position."""
        self.write_raw('\x1b8')

    def hide_cursor(self) -> None:
        """Hide cursor."""
        self.write_raw('\x1b[?25l')

    def show_cursor(self) -> None:
        """Show cursor."""
        self.write_raw('\x1b[?25h')

    def get_columns(self) -> int:
        """Get terminal columns."""
        if self._columns is None:
            self._columns = os.get_terminal_size().columns or 80
        return self._columns

    def get_rows(self) -> int:
        """Get terminal rows."""
        if self._rows is None:
            self._rows = os.get_terminal_size().lines or 24
        return self._rows

    def get_size(self) -> tuple:
        """Get terminal size as (columns, rows)."""
        return (self.get_columns(), self.get_rows())

    def flush(self) -> None:
        """Flush output."""
        self._stream.flush()


# Global output instance
_output: Optional[Output] = None


def get_output() -> Output:
    """Get the global output instance."""
    global _output
    if _output is None:
        _output = Output()
    return _output


def set_output(output: Output) -> None:
    """Set the global output instance."""
    global _output
    _output = output


__all__ = ['Output', 'get_output', 'set_output']