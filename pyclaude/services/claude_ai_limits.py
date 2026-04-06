"""
Claude AI limits service - handles rate limits and quotas for Claude AI subscribers.
"""
from typing import Optional, Dict, Any, Set, Callable, Protocol
from dataclasses import dataclass
from enum import Enum
import time


class QuotaStatus(Enum):
    """Quota status values."""
    ALLOWED = "allowed"
    ALLOWED_WARNING = "allowed_warning"
    REJECTED = "rejected"


class RateLimitType(Enum):
    """Rate limit type values."""
    FIVE_HOUR = "five_hour"
    SEVEN_DAY = "seven_day"
    SEVEN_DAY_OPUS = "seven_day_opus"
    SEVEN_DAY_SONNET = "seven_day_sonnet"
    OVERAGE = "overage"


class OverageDisabledReason(Enum):
    """Reasons why overage is disabled."""
    NOT_PROVISIONED = "overage_not_provisioned"
    ORG_LEVEL_DISABLED = "org_level_disabled"
    OUT_OF_CREDITS = "out_of_credits"
    SEAT_TIER_DISABLED = "seat_tier_level_disabled"
    MEMBER_DISABLED = "member_level_disabled"
    UNKNOWN = "unknown"


@dataclass
class ClaudeAILimits:
    """Claude AI limits state."""
    status: QuotaStatus = QuotaStatus.ALLOWED
    unified_rate_limit_fallback_available: bool = False
    resets_at: Optional[int] = None
    rate_limit_type: Optional[RateLimitType] = None
    utilization: Optional[float] = None
    overage_status: Optional[QuotaStatus] = None
    overage_resets_at: Optional[int] = None
    overage_disabled_reason: Optional[OverageDisabledReason] = None
    is_using_overage: bool = False
    surpassed_threshold: Optional[float] = None


# Current limits state
current_limits: ClaudeAILimits = ClaudeAILimits()

# Status change listeners
status_listeners: Set[Callable[[ClaudeAILimits], None]] = set()


# Early warning configurations
EARLY_WARNING_CONFIGS = [
    {
        'rate_limit_type': RateLimitType.FIVE_HOUR,
        'claim_abbrev': '5h',
        'window_seconds': 5 * 60 * 60,
        'thresholds': [{'utilization': 0.9, 'time_pct': 0.72}],
    },
    {
        'rate_limit_type': RateLimitType.SEVEN_DAY,
        'claim_abbrev': '7d',
        'window_seconds': 7 * 24 * 60 * 60,
        'thresholds': [
            {'utilization': 0.75, 'time_pct': 0.6},
            {'utilization': 0.5, 'time_pct': 0.35},
            {'utilization': 0.25, 'time_pct': 0.15},
        ],
    },
]


def get_rate_limit_display_name(rate_limit_type: RateLimitType) -> str:
    """Get display name for a rate limit type."""
    names = {
        RateLimitType.FIVE_HOUR: 'session limit',
        RateLimitType.SEVEN_DAY: 'weekly limit',
        RateLimitType.SEVEN_DAY_OPUS: 'Opus limit',
        RateLimitType.SEVEN_DAY_SONNET: 'Sonnet limit',
        RateLimitType.OVERAGE: 'extra usage limit',
    }
    return names.get(rate_limit_type, str(rate_limit_type.value))


def emit_status_change(limits: ClaudeAILimits) -> None:
    """Emit a status change event."""
    global current_limits
    current_limits = limits

    for listener in status_listeners:
        listener(limits)


def add_status_listener(listener: Callable[[ClaudeAILimits], None]) -> None:
    """Add a status change listener."""
    status_listeners.add(listener)


def remove_status_listener(listener: Callable[[ClaudeAILimits], None]) -> None:
    """Remove a status change listener."""
    status_listeners.discard(listener)


def compute_time_progress(resets_at: int, window_seconds: int) -> float:
    """Compute what fraction of a time window has elapsed."""
    now_seconds = int(time.time())
    window_start = resets_at - window_seconds
    elapsed = now_seconds - window_start
    return max(0, min(1, elapsed / window_seconds))


def extract_quota_status_from_headers(headers: Dict[str, str]) -> None:
    """Extract quota status from response headers."""
    global current_limits

    status_str = headers.get('anthropic-ratelimit-unified-status', 'allowed')
    try:
        status = QuotaStatus(status_str)
    except ValueError:
        status = QuotaStatus.ALLOWED

    resets_at_header = headers.get('anthropic-ratelimit-unified-reset')
    resets_at = int(reset_at_header) if resets_at_header else None

    unified_fallback = headers.get('anthropic-ratelimit-unified-fallback') == 'available'

    rate_limit_type_str = headers.get('anthropic-ratelimit-unified-representative-claim')
    rate_limit_type = RateLimitType(rate_limit_type_str) if rate_limit_type_str else None

    overage_status_str = headers.get('anthropic-ratelimit-unified-overage-status')
    overage_status = QuotaStatus(overage_status_str) if overage_status_str else None

    new_limits = ClaudeAILimits(
        status=status,
        resets_at=resets_at,
        unified_rate_limit_fallback_available=unified_fallback,
        rate_limit_type=rate_limit_type,
        overage_status=overage_status,
        is_using_overage=status == QuotaStatus.REJECTED and overage_status in (QuotaStatus.ALLOWED, QuotaStatus.ALLOWED_WARNING),
    )

    emit_status_change(new_limits)


async def check_quota_status() -> None:
    """
    Check quota status by making a minimal API request.
    In full implementation, this would call the Claude API.
    """
    # Skip in non-essential traffic mode
    # In full implementation, would check isEssentialTrafficOnly()

    # Skip if not a subscriber
    # In full implementation, would check isClaudeAISubscriber()

    # Skip in non-interactive mode
    # In full implementation, would check getIsNonInteractiveSession()

    pass


# Re-export rate limit message functions
from .rate_limit_messages import (
    get_rate_limit_error_message,
    get_rate_limit_warning,
    get_using_overage_text,
)


__all__ = [
    'QuotaStatus',
    'RateLimitType',
    'OverageDisabledReason',
    'ClaudeAILimits',
    'current_limits',
    'status_listeners',
    'emit_status_change',
    'add_status_listener',
    'remove_status_listener',
    'extract_quota_status_from_headers',
    'check_quota_status',
    'get_rate_limit_display_name',
    'get_rate_limit_error_message',
    'get_rate_limit_warning',
    'get_using_overage_text',
]