"""
Messages utilities.

Message creation and manipulation.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """A message."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = None


def create_user_message(content: str, **kwargs) -> Message:
    """Create user message.

    Args:
        content: Message content
        **kwargs: Additional fields

    Returns:
        User message
    """
    return Message(role=MessageRole.USER, content=content, **kwargs)


def create_assistant_message(content: str, **kwargs) -> Message:
    """Create assistant message.

    Args:
        content: Message content
        **kwargs: Additional fields

    Returns:
        Assistant message
    """
    return Message(role=MessageRole.ASSISTANT, content=content, **kwargs)


def create_system_message(content: str, **kwargs) -> Message:
    """Create system message.

    Args:
        content: Message content
        **kwargs: Additional fields

    Returns:
        System message
    """
    return Message(role=MessageRole.SYSTEM, content=content, **kwargs)


def message_to_dict(msg: Message) -> Dict[str, Any]:
    """Convert message to dict.

    Args:
        msg: Message

    Returns:
        Dict representation
    """
    result = {
        "role": msg.role.value,
        "content": msg.content,
    }
    if msg.name:
        result["name"] = msg.name
    if msg.tool_call_id:
        result["tool_call_id"] = msg.tool_call_id
    return result


__all__ = [
    "MessageRole",
    "Message",
    "create_user_message",
    "create_assistant_message",
    "create_system_message",
    "message_to_dict",
]