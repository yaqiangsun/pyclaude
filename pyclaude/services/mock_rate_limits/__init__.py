"""Mock rate limits service for testing."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class MockRateLimit:
    """Mock rate limit state."""
    requests_remaining: int = 100
    tokens_remaining: int = 50000
    reset_time: float = 0

    def __post_init__(self):
        if self.reset_time == 0:
            self.reset_time = time.time() + 60


_mock_limits: Dict[str, MockRateLimit] = {}


def get_mock_rate_limit(key: str = 'default') -> MockRateLimit:
    """Get mock rate limit for a key."""
    if key not in _mock_limits:
        _mock_limits[key] = MockRateLimit()
    return _mock_limits[key]


def set_mock_rate_limit(key: str, limit: MockRateLimit) -> None:
    """Set mock rate limit."""
    _mock_limits[key] = limit


def reset_mock_rate_limits() -> None:
    """Reset all mock rate limits."""
    _mock_limits.clear()


def should_use_mock_subscription() -> bool:
    """Check if should use mock subscription."""
    return False


def get_mock_subscription_type() -> str:
    """Get mock subscription type."""
    return 'free'


__all__ = [
    'MockRateLimit',
    'get_mock_rate_limit',
    'set_mock_rate_limit',
    'reset_mock_rate_limits',
    'should_use_mock_subscription',
    'get_mock_subscription_type',
]