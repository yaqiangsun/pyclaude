"""Away summary service."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AwaySummary:
    """Summary when user is away."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    tool_use_count: int = 0


def create_away_summary(session_id: str) -> AwaySummary:
    """Create a new away summary."""
    return AwaySummary(
        session_id=session_id,
        start_time=datetime.now(),
    )


def complete_away_summary(summary: AwaySummary) -> AwaySummary:
    """Complete an away summary."""
    summary.end_time = datetime.now()
    return summary


__all__ = ['AwaySummary', 'create_away_summary', 'complete_away_summary']