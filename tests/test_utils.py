"""Tests for utils modules."""
import pytest
from pyclaude.utils.array import intersperse, count, uniq


class TestArrayUtils:
    """Test array utility functions."""

    def test_intersperse(self):
        """Can intersperse elements."""
        result = intersperse([1, 2, 3], lambda i: 0)
        assert result == [1, 0, 2, 0, 3]

    def test_count(self):
        """Can count matching elements."""
        result = count([1, 2, 3, 4], lambda x: x > 2)
        assert result == 2

    def test_uniq(self):
        """Can remove duplicates."""
        result = uniq([1, 2, 2, 3, 3, 3])
        assert result == [1, 2, 3]