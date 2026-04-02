"""
Group tool uses utilities.

Group tool uses by conversation.
"""

from typing import List, Dict, Any
from collections import defaultdict


def group_tool_uses(
    tool_calls: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Group tool uses by conversation.

    Args:
        tool_calls: List of tool calls

    Returns:
        Dict mapping conversation to tool calls
    """
    groups = defaultdict(list)

    for call in tool_calls:
        # Extract conversation ID from call
        conv_id = call.get("conversation_id", "default")
        groups[conv_id].append(call)

    return dict(groups)


def get_tool_use_count(
    tool_calls: List[Dict[str, Any]],
    tool_name: str,
) -> int:
    """Count uses of a specific tool.

    Args:
        tool_calls: List of tool calls
        tool_name: Tool name

    Returns:
        Use count
    """
    return sum(1 for call in tool_calls if call.get("name") == tool_name)


__all__ = [
    "group_tool_uses",
    "get_tool_use_count",
]