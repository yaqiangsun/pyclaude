"""
Stream utilities.

Stream processing helpers.
"""

import asyncio
from typing import AsyncIterator, Callable, Any, Optional


async def stream_map(
    iterable: AsyncIterator,
    fn: Callable[[Any], Any],
) -> AsyncIterator:
    """Map async iterator through function.

    Args:
        iterable: Input async iterator
        fn: Transform function

    Yields:
        Transformed items
    """
    async for item in iterable:
        yield fn(item)


async def stream_filter(
    iterable: AsyncIterator,
    predicate: Callable[[Any], bool],
) -> AsyncIterator:
    """Filter async iterator.

    Args:
        iterable: Input async iterator
        predicate: Filter predicate

    Yields:
        Items that pass predicate
    """
    async for item in iterable:
        if predicate(item):
            yield item


async def stream_take(
    iterable: AsyncIterator,
    count: int,
) -> AsyncIterator:
    """Take first N items from async iterator.

    Args:
        iterable: Input async iterator
        count: Number of items

    Yields:
        First N items
    """
    for _ in range(count):
        try:
            item = await iterable.__anext__()
            yield item
        except StopAsyncIteration:
            break


async def stream_batch(
    iterable: AsyncIterator,
    size: int,
) -> AsyncIterator[list]:
    """Batch async iterator into chunks.

    Args:
        iterable: Input async iterator
        size: Batch size

    Yields:
        Batches of items
    """
    batch = []
    async for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


__all__ = [
    "stream_map",
    "stream_filter",
    "stream_take",
    "stream_batch",
]