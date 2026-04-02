"""
Cron jitter configuration.

GrowthBook-backed cron jitter configuration.
"""

from typing import Dict, Any
from dataclasses import dataclass

HALF_HOUR_MS = 30 * 60 * 1000
THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000

# Default configuration
DEFAULT_CRON_JITTER_CONFIG = {
    "recurringFrac": 0.1,
    "recurringCapMs": 60000,
    "oneShotMaxMs": 300000,
    "oneShotFloorMs": 60000,
    "oneShotMinuteMod": 60,
    "recurringMaxAgeMs": THIRTY_DAYS_MS,
}


@dataclass
class CronJitterConfig:
    """Cron jitter configuration."""
    recurring_frac: float
    recurring_cap_ms: int
    one_shot_max_ms: int
    one_shot_floor_ms: int
    one_shot_minute_mod: int
    recurring_max_age_ms: int


def get_cron_jitter_config() -> Dict[str, Any]:
    """Get cron jitter configuration.

    Returns:
        Cron jitter config dict
    """
    # Placeholder - would fetch from GrowthBook in actual implementation
    return DEFAULT_CRON_JITTER_CONFIG.copy()


__all__ = [
    "CronJitterConfig",
    "DEFAULT_CRON_JITTER_CONFIG",
    "get_cron_jitter_config",
]