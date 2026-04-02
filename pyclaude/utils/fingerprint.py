"""
Fingerprinting utilities.

Generate unique identifiers for sessions/users.
"""

import hashlib
import os
from typing import Optional


def get_machine_fingerprint() -> str:
    """Get machine fingerprint.

    Returns:
        Unique machine identifier
    """
    # Combine various machine identifiers
    parts = [
        os.environ.get("HOSTNAME", ""),
        os.environ.get("USER", ""),
        os.environ.get("HOME", ""),
    ]
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def get_session_fingerprint(session_id: str) -> str:
    """Get session-specific fingerprint.

    Args:
        session_id: Session ID

    Returns:
        Session fingerprint
    """
    machine_fp = get_machine_fingerprint()
    combined = f"{machine_fp}|{session_id}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generate_anonymous_id() -> str:
    """Generate anonymous user ID.

    Returns:
        Anonymous ID
    """
    import random
    import string
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


__all__ = [
    "get_machine_fingerprint",
    "get_session_fingerprint",
    "generate_anonymous_id",
]