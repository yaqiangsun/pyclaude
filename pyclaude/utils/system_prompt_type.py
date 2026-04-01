"""
Branded type for system prompt arrays.

This module is intentionally dependency-free so it can be imported
from anywhere without risking circular initialization issues.
"""

from typing import List, TypeVar, ReadOnly

T = TypeVar('T')


class _SystemPromptMeta(type):
    """Metaclass to create a branded type."""
    pass


class _SystemPrompt(list):
    """Branded type for system prompt arrays."""
    pass


def as_system_prompt(value: List[str]) -> List[str]:
    """Cast a list to system prompt type."""
    return value  # type: ignore