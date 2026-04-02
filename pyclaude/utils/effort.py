"""
Effort level utilities.

Manages effort/quality levels for responses.
"""

from typing import Optional
from enum import Enum


class EffortLevel(str, Enum):
    """Effort/quality levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


# Effort level to token multiplier
EFFORT_TOKEN_MULTIPLIERS = {
    EffortLevel.MINIMAL: 0.5,
    EffortLevel.LOW: 0.75,
    EffortLevel.MEDIUM: 1.0,
    EffortLevel.HIGH: 1.5,
    EffortLevel.MAXIMUM: 2.0,
}


def get_effort_level(effort: Optional[str]) -> EffortLevel:
    """Parse effort level from string.

    Args:
        effort: Effort string (e.g., "high", "medium")

    Returns:
        EffortLevel enum
    """
    if not effort:
        return EffortLevel.MEDIUM

    effort_lower = effort.lower()
    for level in EffortLevel:
        if level.value == effort_lower:
            return level

    return EffortLevel.MEDIUM


def get_token_multiplier(effort: EffortLevel) -> float:
    """Get token multiplier for effort level.

    Args:
        effort: Effort level

    Returns:
        Token multiplier
    """
    return EFFORT_TOKEN_MULTIPLIERS.get(effort, 1.0)


def should_use_high_effort(model: str) -> bool:
    """Check if model should use high effort by default.

    Args:
        model: Model name

    Returns:
        True if high effort recommended
    """
    # Placeholder - would check model capabilities
    return "opus" in model.lower()


__all__ = [
    "EffortLevel",
    "EFFORT_TOKEN_MULTIPLIERS",
    "get_effort_level",
    "get_token_multiplier",
    "should_use_high_effort",
]