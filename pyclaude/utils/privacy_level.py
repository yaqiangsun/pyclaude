"""
Privacy level utilities.

Privacy level configuration.
"""

import os
from typing import Optional


class PrivacyLevel(str, Enum):
    """Privacy levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    MAXIMAL = "maximal"


def get_privacy_level() -> PrivacyLevel:
    """Get current privacy level.

    Returns:
        Privacy level
    """
    level = os.environ.get("CLAUDE_CODE_PRIVACY_LEVEL", "standard").lower()
    if level in ["minimal", "standard", "maximal"]:
        return PrivacyLevel(level)
    return PrivacyLevel.STANDARD


def get_essential_traffic_only_reason() -> Optional[str]:
    """Get reason for essential traffic only mode.

    Returns:
        Environment variable name or None
    """
    # Check various privacy-related env vars
    for var in [
        "CLAUDE_CODE_ESSENTIAL_TRAFFIC_ONLY",
        "RESTRICTED_MODE",
    ]:
        if os.environ.get(var):
            return var
    return None


def should_collect_telemetry() -> bool:
    """Check if telemetry should be collected.

    Returns:
        True if telemetry allowed
    """
    return get_privacy_level() != PrivacyLevel.MAXIMAL


__all__ = [
    "PrivacyLevel",
    "get_privacy_level",
    "get_essential_traffic_only_reason",
    "should_collect_telemetry",
]