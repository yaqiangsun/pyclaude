"""
Sequential utilities.

Run functions sequentially with results.
"""

from typing import TypeVar, Callable, Awaitable, List, Any

T = TypeVar("T")


async def run_sequential(
    fns: List[Callable[..., Awaitable[T]]],
    *args,
    **kwargs,
) -> List[T]:
    """Run async functions sequentially.

    Args:
        fns: List of async functions
        *args: Positional args for each function
        **kwargs: Keyword args for each function

    Returns:
        List of results
    """
    results = []
    for fn in fns:
        result = await fn(*args, **kwargs)
        results.append(result)
    return results


async def run_sequential_with_index(
    fns: List[Callable[[int], Awaitable[T]]],
) -> List[T]:
    """Run async functions sequentially with index.

    Args:
        fns: List of async functions that take index

    Returns:
        List of results
    """
    results = []
    for i, fn in enumerate(fns):
        result = await fn(i)
        results.append(result)
    return results


__all__ = [
    "run_sequential",
    "run_sequential_with_index",
]