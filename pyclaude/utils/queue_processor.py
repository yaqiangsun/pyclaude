"""
Queue processor utilities.

Process items from a queue.
"""

import asyncio
from typing import Callable, Any, Optional, List
from dataclasses import dataclass


@dataclass
class QueueItem:
    """Queue item."""
    id: str
    data: Any
    priority: int = 0


class QueueProcessor:
    """Process items from a queue."""

    def __init__(self, handler: Callable, concurrency: int = 1):
        self.handler = handler
        self.concurrency = concurrency
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._workers: List[asyncio.Task] = []

    async def put(self, item: QueueItem) -> None:
        """Add item to queue.

        Args:
            item: Queue item
        """
        await self._queue.put(item)

    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine.

        Args:
            worker_id: Worker identifier
        """
        while self._running:
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self.handler(item)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception:
                pass

    async def start(self) -> None:
        """Start processing."""
        self._running = True
        for i in range(self.concurrency):
            task = asyncio.create_task(self._worker(i))
            self._workers.append(task)

    async def stop(self) -> None:
        """Stop processing."""
        self._running = False
        for task in self._workers:
            task.cancel()
        self._workers.clear()


__all__ = [
    "QueueItem",
    "QueueProcessor",
]