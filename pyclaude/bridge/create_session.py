"""Create bridge session."""

import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CreateSessionParams:
    """Parameters for creating a session."""
    name: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


async def create_session(params: Optional[CreateSessionParams] = None) -> Dict[str, Any]:
    """Create a new bridge session."""
    params = params or CreateSessionParams()

    session_id = str(uuid.uuid4())

    return {
        'session_id': session_id,
        'name': params.name,
        'metadata': params.metadata,
        'created': True,
    }


__all__ = ['CreateSessionParams', 'create_session']