"""
Auto mode denials tracking.

Tracks commands recently denied by the auto mode classifier.
"""

import os
from typing import List
from dataclasses import dataclass

# Feature flag for transcript classifier
_TRANSCRIPT_CLASSIFIER_ENABLED = os.environ.get("CLAUDE_TRANSCRIPT_CLASSIFIER") == "1"


@dataclass(frozen=True)
class AutoModeDenial:
    """Represents a denial from auto mode classifier."""
    tool_name: str
    display: str  # Human-readable description (e.g. bash command string)
    reason: str
    timestamp: float


# In-memory storage for denials
DENIALS: List[AutoModeDenial] = []
MAX_DENIALS = 20


def record_auto_mode_denial(denial: AutoModeDenial) -> None:
    """Record a denial from the auto mode classifier.

    Args:
        denial: The denial to record
    """
    global DENIALS
    if not _TRANSCRIPT_CLASSIFIER_ENABLED:
        return
    DENIALS = [denial] + DENIALS[:MAX_DENIALS - 1]


def get_auto_mode_denials() -> List[AutoModeDenial]:
    """Get all recorded auto mode denials.

    Returns:
        List of auto mode denials
    """
    return DENIALS.copy()


__all__ = ["AutoModeDenial", "record_auto_mode_denial", "get_auto_mode_denials"]