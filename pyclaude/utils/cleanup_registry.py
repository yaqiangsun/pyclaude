"""
Cleanup registry.

Global registry for cleanup functions that should run during graceful shutdown.
"""

from typing import Callable, Awaitable, Set

# Global registry for cleanup functions
_cleanup_functions: Set[Callable[[], Awaitable[None]]] = set()


def register_cleanup(cleanup_fn: Callable[[], Awaitable[None]]) -> Callable[[], None]:
    """Register a cleanup function to run during graceful shutdown.

    Args:
        cleanup_fn: Function to run during cleanup (can be sync or async)

    Returns:
        Unregister function that removes the cleanup handler
    """
    _cleanup_functions.add(cleanup_fn)

    def unregister() -> None:
        _cleanup_functions.discard(cleanup_fn)

    return unregister


async def run_cleanup_functions() -> None:
    """Run all registered cleanup functions.

    Used internally by graceful shutdown.
    """
    await asyncio.gather(*[fn() for fn in _cleanup_functions], return_exceptions=True)


import asyncio


__all__ = ["register_cleanup", "run_cleanup_functions"]