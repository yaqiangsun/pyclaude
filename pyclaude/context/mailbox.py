"""Mailbox context for queued messages."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessagePriority(str, Enum):
    """Message priority."""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'


@dataclass
class QueuedMessage:
    """A queued message."""
    id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MailboxContext:
    """Context for managing queued messages."""

    def __init__(self):
        self._queue: List[QueuedMessage] = []
        self._processing = False

    def enqueue(self, message: QueuedMessage) -> None:
        """Add a message to the queue."""
        self._queue.append(message)
        self._queue.sort(key=lambda m: (
            0 if m.priority == MessagePriority.URGENT else
            1 if m.priority == MessagePriority.HIGH else
            2 if m.priority == MessagePriority.NORMAL else 3
        ))

    def dequeue(self) -> Optional[QueuedMessage]:
        """Remove and return the first message."""
        if self._queue:
            return self._queue.pop(0)
        return None

    def peek(self) -> Optional[QueuedMessage]:
        """View the first message without removing."""
        if self._queue:
            return self._queue[0]
        return None

    def get_queue(self) -> List[QueuedMessage]:
        """Get all queued messages."""
        return list(self._queue)

    def clear(self) -> None:
        """Clear the queue."""
        self._queue.clear()

    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self._processing

    def set_processing(self, processing: bool) -> None:
        """Set processing state."""
        self._processing = processing


# Global context
_mailbox_context = MailboxContext()


def get_mailbox_context() -> MailboxContext:
    """Get the global mailbox context."""
    return _mailbox_context


__all__ = ['MessagePriority', 'QueuedMessage', 'MailboxContext', 'get_mailbox_context']