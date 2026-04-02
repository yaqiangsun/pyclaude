"""
Sleep utilities.

Async sleep helpers.
"""

import asyncio
from typing import Awaitable, Callable, Optional


async def sleep_ms(milliseconds: int) -> None:
    """Sleep for specified milliseconds.

    Args:
        milliseconds: Sleep duration in ms
    """
    await asyncio.sleep(milliseconds / 1000)


async def sleep_until( timestamp: float) -> None:
    """Sleep until a specific timestamp.

    Args:
        timestamp: Unix timestamp to sleep until
    """
    import time
    delay = timestamp - time.time()
    if delay > 0:
        await asyncio.sleep(delay)


async def retry_with_backoff(
    fn: Callable,
    max_retries: int = 3,
    initial_delay_ms: int = 100,
    max_delay_ms: int = 5000,
) -> any:
    """Retry function with exponential backoff.

    Args:
        fn: Async function to retry
        max_retries: Maximum retry attempts
        initial_delay_ms: Initial delay in ms
        max_delay_ms: Maximum delay in ms

    Returns:
        Function result
    """
    delay = initial_delay_ms
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception:
            if attempt == max_retries - 1:
                raise
            await sleep_ms(delay)
            delay = min(delay * 2, max_delay_ms)


__all__ = [
    "sleep_ms",
    "sleep_until",
    "retry_with_backoff",
]