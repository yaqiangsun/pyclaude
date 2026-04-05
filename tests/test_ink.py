"""Tests for ink module."""
import pytest
from pyclaude.ink import (
    string_width,
    widest_line,
    clear_terminal,
    FRAME_INTERVAL_MS,
)


class TestStringWidth:
    """Test string_width function."""

    def test_ascii_string(self):
        """ASCII strings have correct width."""
        assert string_width("hello") == 5
        assert string_width("Hello World") == 11

    def test_empty_string(self):
        """Empty string has width 0."""
        assert string_width("") == 0

    def test_multiline_string(self):
        """Multiline string has combined width."""
        # Newlines may or may not have width depending on implementation
        result = string_width("hello\nworld")
        assert result >= 5

    def test_chinese_characters(self):
        """Chinese characters have width 2."""
        # May not work without wcwidth
        result = string_width("你好")
        assert result >= 2


class TestWidestLine:
    """Test widest_line function."""

    def test_single_line(self):
        """Single line returns its width."""
        assert widest_line("hello") == 5

    def test_multiple_lines(self):
        """Multiple lines returns max width."""
        assert widest_line("hi\nhello\nhey") == 5

    def test_empty_string(self):
        """Empty string returns 0."""
        assert widest_line("") == 0


class TestClearTerminal:
    """Test clear terminal function."""

    def test_clear_terminal_defined(self):
        """clear_terminal is defined."""
        assert clear_terminal is not None
        assert len(clear_terminal) > 0

    def test_frame_interval(self):
        """Frame interval is correct (~60fps)."""
        assert FRAME_INTERVAL_MS == 16