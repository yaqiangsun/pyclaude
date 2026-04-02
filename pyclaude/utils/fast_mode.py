"""
Fast mode utilities.

Manages fast/quality mode tradeoff.
"""

import os
from typing import Optional


def is_fast_mode_enabled() -> bool:
    """Check if fast mode is enabled.

    Returns:
        True if fast mode is on
    """
    return os.environ.get("CLAUDE_CODE_FAST_MODE", "").lower() in ("1", "true", "yes")


def is_quota_enabled() -> bool:
    """Check if quota mode is enabled.

    Returns:
        True if quota mode is on
    """
    return os.environ.get("CLAUDE_CODE_QUOTA_MODE", "").lower() in ("1", "true", "yes")


def get_quota_remaining() -> Optional[float]:
    """Get remaining quota.

    Returns:
        Remaining quota or None
    """
    # Placeholder
    return None


def should_use_fast_model(task_type: str) -> bool:
    """Determine if fast model should be used.

    Args:
        task_type: Type of task

    Returns:
        True if fast model recommended
    """
    # Simple heuristic
    fast_tasks = ["read", "grep", "simple"]
    return any(t in task_type.lower() for t in fast_tasks)


__all__ = [
    "is_fast_mode_enabled",
    "is_quota_enabled",
    "get_quota_remaining",
    "should_use_fast_model",
]