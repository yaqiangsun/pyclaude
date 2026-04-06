"""
Rate limit mocking service for testing rate limit handling.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class RateLimitMockMode(Enum):
    """Mode for rate limit mocking."""
    OFF = "off"
    ENABLED = "enabled"
    FOREVER = "forever"  # Always return rate limit


@dataclass
class RateLimitMock:
    """Mock rate limit configuration."""
    enabled: bool = False
    # Headers to return for rate limiting
    status: str = "rejected"
    reset: Optional[int] = None
    utilization: Optional[float] = None
    overage_status: Optional[str] = None


# Global mock state
_mock: RateLimitMock = RateLimitMock()


def should_process_rate_limits(is_subscriber: bool) -> bool:
    """
    Check if rate limits should be processed.

    Args:
        is_subscriber: Whether the user is a subscriber

    Returns:
        True if rate limits should be processed
    """
    return is_subscriber or _mock.enabled


def enable_rate_limit_mock(
    status: str = "rejected",
    reset: Optional[int] = None,
    utilization: Optional[float] = None,
) -> None:
    """Enable rate limit mocking."""
    global _mock
    _mock = RateLimitMock(
        enabled=True,
        status=status,
        reset=reset,
        utilization=utilization,
    )


def disable_rate_limit_mock() -> None:
    """Disable rate limit mocking."""
    global _mock
    _mock = RateLimitMock()


def is_rate_limit_mock_enabled() -> bool:
    """Check if rate limit mocking is enabled."""
    return _mock.enabled


def process_rate_limit_headers(headers: Any) -> Any:
    """
    Process rate limit headers, applying mocks if enabled.

    Args:
        headers: Original headers object

    Returns:
        Processed headers (or mock headers if mocking)
    """
    if not _mock.enabled:
        return headers

    # In full implementation, would create mock headers
    # For now, just return the original headers with modifications
    return headers


def get_mock_reset_time() -> Optional[int]:
    """Get the mock reset time."""
    return _mock.reset


def get_mock_utilization() -> Optional[float]:
    """Get the mock utilization."""
    return _mock.utilization


__all__ = [
    'RateLimitMockMode',
    'RateLimitMock',
    'should_process_rate_limits',
    'enable_rate_limit_mock',
    'disable_rate_limit_mock',
    'is_rate_limit_mock_enabled',
    'process_rate_limit_headers',
]