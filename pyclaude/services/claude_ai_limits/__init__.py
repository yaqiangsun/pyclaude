"""Claude AI limits service."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ClaudeAILimits:
    """Rate limits for Claude API."""
    max_requests_per_minute: int = 50
    max_tokens_per_minute: int = 100000
    max_tokens_per_day: int = 1000000
    max_concurrent_requests: int = 5


# Default limits
DEFAULT_LIMITS = ClaudeAILimits()


def get_claude_ai_limits() -> ClaudeAILimits:
    """Get Claude AI rate limits."""
    return DEFAULT_LIMITS


def update_limits(limits: Dict[str, Any]) -> None:
    """Update rate limits."""
    global DEFAULT_LIMITS
    if 'max_requests_per_minute' in limits:
        DEFAULT_LIMITS.max_requests_per_minute = limits['max_requests_per_minute']
    if 'max_tokens_per_minute' in limits:
        DEFAULT_LIMITS.max_tokens_per_minute = limits['max_tokens_per_minute']
    if 'max_tokens_per_day' in limits:
        DEFAULT_LIMITS.max_tokens_per_day = limits['max_tokens_per_day']
    if 'max_concurrent_requests' in limits:
        DEFAULT_LIMITS.max_concurrent_requests = limits['max_concurrent_requests']


__all__ = ['ClaudeAILimits', 'DEFAULT_LIMITS', 'get_claude_ai_limits', 'update_limits']