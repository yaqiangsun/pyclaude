"""
Generates a short session recap for the "while you were away" card.
"""
from typing import List, Optional, Protocol
import asyncio

# Recap only needs recent context — truncate to avoid "prompt too long" on
# large sessions. 30 messages ≈ ~15 exchanges, plenty for "where we left off."
RECENT_MESSAGE_WINDOW = 30


def build_away_summary_prompt(memory: Optional[str]) -> str:
    """Build the prompt for generating away summary."""
    memory_block = f"Session memory (broader context):\n{memory}\n\n" if memory else ""
    return f"{memory_block}The user stepped away and is coming back. Write exactly 1-3 short sentences. Start by stating the high-level task — what they are building or debugging, not implementation details. Next: the concrete next step. Skip status reports and commit recaps."


class Message(Protocol):
    """Protocol for message type."""
    role: str
    content: str


async def generate_away_summary(
    messages: List[Message],
    signal: Optional[asyncio.Event] = None,
) -> Optional[str]:
    """
    Generates a short session recap for the "while you were away" card.
    Returns None on abort, empty transcript, or error.

    Args:
        messages: List of conversation messages
        signal: Optional abort signal

    Returns:
        The away summary text, or None if generation failed
    """
    if not messages:
        return None

    # Check if aborted
    if signal and signal.is_set():
        return None

    try:
        # For now, return a placeholder since we need the full API integration
        # In a full implementation, this would call the Claude API
        recent = messages[-RECENT_MESSAGE_WINDOW:] if len(messages) > RECENT_MESSAGE_WINDOW else messages

        # Build the summary prompt
        prompt = build_away_summary_prompt(None)  # memory would come from session memory

        # Placeholder return - would need full queryModelWithoutStreaming implementation
        return None

    except Exception:
        return None


# Re-export for compatibility
__all__ = ['generate_away_summary', 'build_away_summary_prompt', 'RECENT_MESSAGE_WINDOW']