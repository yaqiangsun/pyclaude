"""
Message queue manager utilities.

Manage multiple message queues.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class QueueItem:
    """Queue item."""
    id: str
    data: Any
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    retries: int = 0


class MessageQueue:
    """Priority message queue."""

    def __init__(self, name: str, max_size: int = 1000):
        self.name = name
        self.max_size = max_size
        self._queue: List[QueueItem] = []
        self._lock = asyncio.Lock()

    async def enqueue(self, item: QueueItem) -> bool:
        """Add item to queue.

        Args:
            item: Queue item

        Returns:
            True if enqueued
        """
        async with self._lock:
            if len(self._queue) >= self.max_size:
                return False
            self._queue.append(item)
            self._queue.sort(key=lambda x: x.priority, reverse=True)
            return True

    async def dequeue(self) -> Optional[QueueItem]:
        """Remove and return highest priority item.

        Returns:
            Queue item or None
        """
        async with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None

    async def peek(self) -> Optional[QueueItem]:
        """Get highest priority item without removing.

        Returns:
            Queue item or None
        """
        async with self._lock:
            return self._queue[0] if self._queue else None

    async def size(self) -> int:
        """Get queue size.

        Returns:
            Number of items
        """
        async with self._lock:
            return len(self._queue)


# Global queues
_queues: Dict[str, MessageQueue] = {}


def get_queue(name: str, max_size: int = 1000) -> MessageQueue:
    """Get or create a queue.

    Args:
        name: Queue name
        max_size: Maximum queue size

    Returns:
        Queue instance
    """
    if name not in _queues:
        _queues[name] = MessageQueue(name, max_size)
    return _queues[name]


__all__ = [
    "QueueItem",
    "MessageQueue",
    "get_queue",
]