"""
Claude AI Limits Hook - React hook for accessing Claude AI limits.
"""
from typing import Optional, Dict, Any
from .claude_ai_limits import (
    ClaudeAILimits,
    QuotaStatus,
    current_limits,
    add_status_listener,
    remove_status_listener,
    extract_quota_status_from_headers,
)


class UseClaudeAILimits:
    """Hook for accessing Claude AI limits state."""

    def __init__(self):
        self._limits = current_limits
        self._listeners = []

    def get_limits(self) -> ClaudeAILimits:
        """Get current limits."""
        return self._limits

    def get_status(self) -> QuotaStatus:
        """Get current quota status."""
        return self._limits.status

    def is_allowed(self) -> bool:
        """Check if requests are allowed."""
        return self._limits.status in (QuotaStatus.ALLOWED, QuotaStatus.ALLOWED_WARNING)

    def is_warning(self) -> bool:
        """Check if there's a warning."""
        return self._limits.status == QuotaStatus.ALLOWED_WARNING

    def is_rejected(self) -> bool:
        """Check if requests are rejected."""
        return self._limits.status == QuotaStatus.REJECTED

    def get_resets_at(self) -> Optional[int]:
        """Get reset timestamp."""
        return self._limits.resets_at

    def get_utilization(self) -> Optional[float]:
        """Get current utilization."""
        return self._limits.utilization

    def is_using_overage(self) -> bool:
        """Check if using overage credits."""
        return self._limits.is_using_overage


def use_claude_ai_limits() -> UseClaudeAILimits:
    """
    React-style hook for accessing Claude AI limits.

    Returns:
        UseClaudeAILimits instance with limit state
    """
    return UseClaudeAILimits()


__all__ = [
    'use_claude_ai_limits',
    'UseClaudeAILimits',
    'ClaudeAILimits',
    'QuotaStatus',
]