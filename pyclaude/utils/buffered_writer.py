"""
Buffered writer utilities.

Provides buffered writing with configurable flush intervals.
"""

import asyncio
from typing import Callable, List, Optional
from dataclasses import dataclass


WriteFn = Callable[[str], None]


@dataclass
class BufferedWriter:
    """Buffered writer interface."""
    write: Callable[[str], None]
    flush: Callable[[], None]
    dispose: Callable[[], None]


def create_buffered_writer(
    write_fn: WriteFn,
    flush_interval_ms: int = 1000,
    max_buffer_size: int = 100,
    max_buffer_bytes: int = float('inf'),
    immediate_mode: bool = False,
) -> BufferedWriter:
    """Create a buffered writer.

    Args:
        write_fn: Function to write content
        flush_interval_ms: Flush interval in milliseconds
        max_buffer_size: Maximum number of items in buffer
        max_buffer_bytes: Maximum bytes in buffer
        immediate_mode: If True, write immediately without buffering

    Returns:
        BufferedWriter instance
    """
    buffer: List[str] = []
    buffer_bytes = 0
    flush_timer: Optional[asyncio.TimerHandle] = None
    pending_overflow: Optional[List[str]] = None

    def clear_timer() -> None:
        nonlocal flush_timer
        if flush_timer:
            flush_timer.cancel()
            flush_timer = None

    def flush() -> None:
        nonlocal buffer, buffer_bytes, pending_overflow
        if pending_overflow:
            write_fn("".join(pending_overflow))
            pending_overflow = None
        if not buffer:
            return
        write_fn("".join(buffer))
        buffer = []
        buffer_bytes = 0
        clear_timer()

    def schedule_flush() -> None:
        nonlocal flush_timer
        if not flush_timer:
            loop = asyncio.get_event_loop()
            flush_timer = loop.call_later(
                flush_interval_ms / 1000.0,
                flush
            )

    def flush_deferred() -> None:
        nonlocal buffer, buffer_bytes, pending_overflow, flush_timer
        if pending_overflow:
            # Coalesce into existing pending overflow
            pending_overflow.extend(buffer)
            buffer = []
            buffer_bytes = 0
            clear_timer()
            return

        # Detach buffer synchronously
        detached = buffer
        buffer = []
        buffer_bytes = 0
        clear_timer()
        pending_overflow = detached

        # Schedule async flush
        loop = asyncio.get_event_loop()
        loop.call_soon(lambda: write_fn("".join(pending_overflow)) if pending_overflow else None)
        pending_overflow = None

    def write(content: str) -> None:
        if immediate_mode:
            write_fn(content)
            return

        buffer.append(content)
        buffer_bytes += len(content)
        schedule_flush()

        if len(buffer) >= max_buffer_size or buffer_bytes >= max_buffer_bytes:
            flush_deferred()

    def dispose() -> None:
        flush()

    return BufferedWriter(write=write, flush=flush, dispose=dispose)


__all__ = ["BufferedWriter", "create_buffered_writer"]