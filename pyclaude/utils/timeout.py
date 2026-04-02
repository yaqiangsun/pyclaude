"""
Timeout utilities.

Timeout and deadline helpers.
"""

import asyncio
from typing import Optional, Any, Callable, TypeVar
from functools import wraps

T = TypeVar("T")


async def with_timeout(coro, timeout_ms: int):
    """Run coroutine with timeout.

    Args:
        coro: Coroutine to run
        timeout_ms: Timeout in milliseconds

    Returns:
        Result of coroutine

    Raises:
        asyncio.TimeoutError: If timeout exceeded
    """
    return await asyncio.wait_for(coro, timeout=timeout_ms / 1000)


def timeout_after(ms: int):
    """Decorator to add timeout to async function.

    Args:
        ms: Timeout in milliseconds
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await with_timeout(func(*args, **kwargs), ms)
        return wrapper
    return decorator


class Deadline:
    """Deadline timer."""

    def __init__(self, timeout_ms: int):
        self.timeout_ms = timeout_ms
        self.start = asyncio.get_event_loop().time() * 1000

    def remaining(self) -> float:
        """Get remaining time in ms."""
        elapsed = asyncio.get_event_loop().time() * 1000 - self.start
        return max(0, self.timeout_ms - elapsed)

    def is_expired(self) -> bool:
        """Check if deadline expired."""
        return self.remaining() <= 0


__all__ = [
    "with_timeout",
    "timeout_after",
    "Deadline",
]