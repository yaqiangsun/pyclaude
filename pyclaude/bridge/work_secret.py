"""Work secret management."""

import os
import secrets
from typing import Optional, Dict, Any


_work_secrets: Dict[str, str] = {}


def generate_work_secret() -> str:
    """Generate a new work secret."""
    return secrets.token_urlsafe(32)


def set_work_secret(session_id: str, secret: str) -> None:
    """Set work secret for a session."""
    _work_secrets[session_id] = secret


def get_work_secret(session_id: str) -> Optional[str]:
    """Get work secret for a session."""
    return _work_secrets.get(session_id)


def clear_work_secret(session_id: str) -> bool:
    """Clear work secret for a session."""
    if session_id in _work_secrets:
        del _work_secrets[session_id]
        return True
    return False


def validate_work_secret(session_id: str, secret: str) -> bool:
    """Validate a work secret."""
    stored = get_work_secret(session_id)
    if not stored:
        return False
    return secrets.compare_digest(stored, secret)


__all__ = [
    'generate_work_secret',
    'set_work_secret',
    'get_work_secret',
    'clear_work_secret',
    'validate_work_secret',
]