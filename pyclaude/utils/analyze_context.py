"""
Analyze context utilities.

Context analysis for prompts.
"""

from typing import Dict, Any, List


def analyze_context(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze conversation context.

    Args:
        messages: Conversation messages

    Returns:
        Context analysis
    """
    total_tokens = 0
    tool_calls = 0

    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total_tokens += len(content) // 4
        tool_calls += len(msg.get("tool_calls", []))

    return {
        "message_count": len(messages),
        "estimated_tokens": total_tokens,
        "tool_calls": tool_calls,
    }


__all__ = ["analyze_context"]