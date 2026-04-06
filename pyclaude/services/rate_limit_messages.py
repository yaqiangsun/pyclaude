"""
Rate limit messages service - provides user-facing messages for rate limits.
"""
from typing import Optional


def get_rate_limit_error_message(
    rate_limit_type: str,
    resets_at: Optional[int] = None,
) -> str:
    """
    Get the error message for a rate limit.

    Args:
        rate_limit_type: Type of rate limit (five_hour, seven_day, etc.)
        resets_at: Unix timestamp when the limit resets

    Returns:
        Error message string
    """
    messages = {
        'five_hour': "You've reached your session message limit. Please wait before continuing.",
        'seven_day': "You've reached your weekly message limit. Please wait before continuing.",
        'seven_day_opus': "You've reached your Opus model limit for this week.",
        'seven_day_sonnet': "You've reached your Sonnet model limit for this week.",
        'overage': "You've exceeded your usage limit.",
    }

    base_message = messages.get(rate_limit_type, "Rate limit reached.")

    if resets_at:
        from datetime import datetime
        reset_time = datetime.fromtimestamp(resets_at)
        reset_str = reset_time.strftime("%H:%M")
        base_message += f" Resets at {reset_str}."

    return base_message


def get_rate_limit_warning(
    rate_limit_type: str,
    utilization: float,
    resets_at: Optional[int] = None,
) -> str:
    """
    Get the warning message for approaching rate limit.

    Args:
        rate_limit_type: Type of rate limit
        utilization: Current utilization (0-1)
        resets_at: Unix timestamp when the limit resets

    Returns:
        Warning message string
    """
    percent = int(utilization * 100)
    claim_name = {
        'five_hour': 'session',
        'seven_day': 'weekly',
        'seven_day_opus': 'Opus',
        'seven_day_sonnet': 'Sonnet',
        'overage': 'extra usage',
    }.get(rate_limit_type, 'message')

    message = f"You're at {percent}% of your {claim_name} limit."

    if resets_at:
        from datetime import datetime
        reset_time = datetime.fromtimestamp(resets_at)
        reset_str = reset_time.strftime("%H:%M")
        message += f" Resets at {reset_str}."

    return message


def get_using_overage_text() -> str:
    """Get the message shown when using overage."""
    return "You're now using extra usage credits."


__all__ = [
    'get_rate_limit_error_message',
    'get_rate_limit_warning',
    'get_using_overage_text',
]