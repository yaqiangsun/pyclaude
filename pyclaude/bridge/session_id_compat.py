"""Session ID compatibility."""

from typing import Optional


def normalize_session_id(session_id: str) -> str:
    """Normalize session ID format."""
    # Remove common prefixes if present
    if session_id.startswith('sess-'):
        return session_id[5:]
    return session_id


def format_session_id(session_id: str) -> str:
    """Format session ID with standard prefix."""
    if '-' in session_id:
        return session_id
    return f"sess-{session_id}"


def is_valid_session_id(session_id: str) -> bool:
    """Check if session ID is valid."""
    if not session_id:
        return False
    # Basic validation - should be non-empty and reasonable length
    return len(session_id) >= 8 and len(session_id) <= 64


__all__ = ['normalize_session_id', 'format_session_id', 'is_valid_session_id']