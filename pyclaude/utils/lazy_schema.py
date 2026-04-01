"""
Returns a memoized factory function that constructs the value on first call.
Used to defer Zod schema construction from module init time to first access.
"""

from typing import Callable, TypeVar, Optional

T = TypeVar('T')


def lazy_schema(factory: Callable[[], T]) -> Callable[[], T]:
    """Returns a memoized factory function that constructs the value on first call."""
    cached: Optional[T] = None

    def wrapper() -> T:
        nonlocal cached
        if cached is None:
            cached = factory()
        return cached

    return wrapper