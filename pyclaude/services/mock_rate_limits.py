"""
Mock rate limits service for testing rate limit scenarios.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time


# Mock rate limit data
class MockRateLimitsData:
    """Data class for mock rate limits."""

    def __init__(self):
        self.enabled: bool = False
        self.status: str = "allowed"
        self.resets_at: Optional[int] = None
        self.utilization: Optional[float] = None
        self.overage_status: Optional[str] = None
        self.rate_limit_type: Optional[str] = None
        self.unified_fallback_available: bool = False


_mock_data = MockRateLimitsData()


def get_mock_rate_limits() -> MockRateLimitsData:
    """Get the current mock rate limits data."""
    return _mock_data


def set_mock_rate_limits(
    status: str = "allowed",
    resets_at: Optional[int] = None,
    utilization: Optional[float] = None,
    rate_limit_type: Optional[str] = None,
    overage_status: Optional[str] = None,
) -> None:
    """
    Set mock rate limits.

    Args:
        status: Rate limit status
        resets_at: Unix timestamp when limit resets
        utilization: Current utilization (0-1)
        rate_limit_type: Type of rate limit
        overage_status: Status of overage
    """
    _mock_data.enabled = True
    _mock_data.status = status
    _mock_data.resets_at = resets_at
    _mock_data.utilization = utilization
    _mock_data.rate_limit_type = rate_limit_type
    _mock_data.overage_status = overage_status


def clear_mock_rate_limits() -> None:
    """Clear all mock rate limits."""
    global _mock_data
    _mock_data = MockRateLimitsData()


def is_mock_rate_limits_enabled() -> bool:
    """Check if mock rate limits are enabled."""
    return _mock_data.enabled


# Convenience functions for common test scenarios
def mock_session_limit_reached() -> None:
    """Mock a session rate limit being reached."""
    set_mock_rate_limits(
        status="rejected",
        resets_at=int(time.time()) + 3600,  # 1 hour
        rate_limit_type="five_hour",
    )


def mock_weekly_limit_reached() -> None:
    """Mock a weekly rate limit being reached."""
    set_mock_rate_limits(
        status="rejected",
        resets_at=int(time.time()) + 7 * 24 * 3600,  # 1 week
        rate_limit_type="seven_day",
    )


def mock_warning_threshold(utilization: float = 0.9) -> None:
    """Mock a warning threshold scenario."""
    set_mock_rate_limits(
        status="allowed_warning",
        utilization=utilization,
        resets_at=int(time.time()) + 3600,
        rate_limit_type="five_hour",
    )


__all__ = [
    'MockRateLimitsData',
    'get_mock_rate_limits',
    'set_mock_rate_limits',
    'clear_mock_rate_limits',
    'is_mock_rate_limits_enabled',
    'mock_session_limit_reached',
    'mock_weekly_limit_reached',
    'mock_warning_threshold',
]