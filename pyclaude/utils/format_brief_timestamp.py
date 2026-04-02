"""
Format brief timestamp utilities.

Short timestamp formatting.
"""

from datetime import datetime, timedelta
from typing import Optional


def format_brief_timestamp(timestamp: float) -> str:
    """Format timestamp as brief string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Brief timestamp string
    """
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}d"
    else:
        return dt.strftime("%m/%d")


__all__ = ["format_brief_timestamp"]