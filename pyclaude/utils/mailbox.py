"""
Mailbox utilities.

Message queue/mailbox pattern implementation.
"""

from typing import Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio


@dataclass
class Message:
    """A mailbox message."""
    id: str
    sender: str
    recipient: str
    content: Any
    timestamp: datetime
    read: bool = False


class Mailbox:
    """Simple mailbox/queue implementation."""

    def __init__(self, name: str):
        self.name = name
        self.messages: List[Message] = []
        self._handlers: List[Callable] = []

    async def send(
        self,
        recipient: str,
        content: Any,
        sender: str = "system",
    ) -> Message:
        """Send a message.

        Args:
            recipient: Message recipient
            content: Message content
            sender: Message sender

        Returns:
            The sent message
        """
        import uuid
        msg = Message(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            content=content,
            timestamp=datetime.now(),
        )
        self.messages.append(msg)

        # Notify handlers
        for handler in self._handlers:
            await handler(msg)

        return msg

    def receive(self, recipient: str) -> List[Message]:
        """Receive messages for recipient.

        Args:
            recipient: Recipient to get messages for

        Returns:
            List of messages
        """
        messages = [m for m in self.messages if m.recipient == recipient]
        for msg in messages:
            msg.read = True
        return messages

    def on_message(self, handler: Callable) -> None:
        """Register message handler.

        Args:
            handler: Async function to call on new messages
        """
        self._handlers.append(handler)


# Global mailboxes
_mailboxes: dict = {}


def get_mailbox(name: str) -> Mailbox:
    """Get or create a mailbox.

    Args:
        name: Mailbox name

    Returns:
        Mailbox instance
    """
    if name not in _mailboxes:
        _mailboxes[name] = Mailbox(name)
    return _mailboxes[name]


__all__ = [
    "Message",
    "Mailbox",
    "get_mailbox",
]