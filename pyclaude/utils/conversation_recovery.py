"""
Conversation recovery utilities.

Handles recovery from conversation interruptions.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ConversationState:
    """State of a conversation."""
    session_id: str
    messages: List[Dict[str, Any]]
    last_message_index: int


def save_conversation_state(
    session_id: str,
    messages: List[Dict[str, Any]],
) -> None:
    """Save conversation state for recovery.

    Args:
        session_id: Session ID
        messages: Conversation messages
    """
    pass


def load_conversation_state(session_id: str) -> Optional[ConversationState]:
    """Load conversation state for recovery.

    Args:
        session_id: Session ID

    Returns:
        Conversation state or None
    """
    return None


def clear_conversation_state(session_id: str) -> None:
    """Clear saved conversation state.

    Args:
        session_id: Session ID
    """
    pass


def get_recovery_candidates() -> List[str]:
    """Get list of sessions that can be recovered.

    Returns:
        List of session IDs
    """
    return []


__all__ = [
    "ConversationState",
    "save_conversation_state",
    "load_conversation_state",
    "clear_conversation_state",
    "get_recovery_candidates",
]