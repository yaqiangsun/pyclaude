"""
Teammate utilities.

Teammate agent management.
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class TeammateMode(str, Enum):
    """Teammate spawn modes."""
    AUTO = "auto"
    TMUX = "tmux"
    IN_PROCESS = "in-process"


@dataclass
class Teammate:
    """A teammate agent."""
    id: str
    name: str
    model: Optional[str] = None
    status: str = "idle"
    session_id: Optional[str] = None


def get_teammate_mode() -> TeammateMode:
    """Get teammate mode from config.

    Returns:
        Teammate mode
    """
    mode = os.environ.get("CLAUDE_CODE_TEAMMATE_MODE", "auto").lower()
    if mode in ["auto", "tmux", "in-process"]:
        return TeammateMode(mode)
    return TeammateMode.AUTO


def list_teammates() -> List[Teammate]:
    """List active teammates.

    Returns:
        List of teammates
    """
    # Placeholder - would get from state
    return []


def create_teammate(name: str, model: Optional[str] = None) -> Teammate:
    """Create a new teammate.

    Args:
        name: Teammate name
        model: Model to use

    Returns:
        Created teammate
    """
    import uuid
    return Teammate(
        id=str(uuid.uuid4()),
        name=name,
        model=model,
    )


__all__ = [
    "TeammateMode",
    "Teammate",
    "get_teammate_mode",
    "list_teammates",
    "create_teammate",
]