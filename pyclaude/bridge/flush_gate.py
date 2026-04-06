"""Flush gate for message batching."""

import asyncio
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class FlushMode(str, Enum):
    """Flush mode for the gate."""
    IMMEDIATE = 'immediate'
    BATCH = 'batch'
    DEBOUNCE = 'debounce'


@dataclass
class FlushGate:
    """Gate for controlling message flushing."""
    mode: FlushMode = FlushMode.BATCH
    batch_size: int = 10
    debounce_ms: int = 100
    _pending: list = field(default_factory=list)
    _flush_task: Optional[asyncio.Task] = None

    def __post_init__(self):
        self._lock = asyncio.Lock()

    async def add(self, item: Any) -> None:
        """Add item to the gate."""
        async with self._lock:
            self._pending.append(item)

            if self.mode == FlushMode.IMMEDIATE:
                await self.flush()
            elif self.mode == FlushMode.DEBOUNCE:
                await self._schedule_debounce_flush()

    async def flush(self) -> list:
        """Flush all pending items."""
        async with self._lock:
            items = list(self._pending)
            self._pending.clear()
            return items

    async def _schedule_debounce_flush(self) -> None:
        """Schedule a debounced flush."""
        if self._flush_task and not self._flush_task.done():
            return

        async def delayed_flush():
            await asyncio.sleep(self.debounce_ms / 1000)
            await self.flush()

        self._flush_task = asyncio.create_task(delayed_flush())

    async def wait_for_flush(self, timeout: Optional[float] = None) -> list:
        """Wait for pending items to be flushed."""
        if not self._pending:
            return []

        if self._flush_task:
            try:
                await asyncio.wait_for(self._flush_task, timeout=timeout)
            except asyncio.TimeoutError:
                pass

        return await self.flush()


# Global flush gate instance
_flush_gate = FlushGate()


def get_flush_gate() -> FlushGate:
    """Get the global flush gate."""
    return _flush_gate


__all__ = ['FlushMode', 'FlushGate', 'get_flush_gate']