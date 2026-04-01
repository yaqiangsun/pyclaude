"""
Worktree mode is now unconditionally enabled for all users.
"""

from typing import Callable, Dict, Iterable, List, TypeVar, Any

T = TypeVar('T')
K = TypeVar('K')


def is_worktree_mode_enabled() -> bool:
    """Check if worktree mode is enabled."""
    return True