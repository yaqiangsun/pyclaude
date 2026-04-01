"""
Message predicates for type checking.

tool_result messages share type:'user' with human turns; the discriminant
is the optional toolUseResult field.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.message import Message, UserMessage


def is_human_turn(m: "Message") -> bool:
    """Check if message is a human turn (not a tool result)."""
    return m.get("type") == "user" and not m.get("isMeta") and m.get("toolUseResult") is None