"""
Circular buffer implementation.
"""

from typing import Generic, TypeVar, List

T = TypeVar('T')


class CircularBuffer(Generic[T]):
    """A fixed-size circular buffer that automatically evicts the oldest items
    when the buffer is full. Useful for maintaining a rolling window of data.
    """

    def __init__(self, capacity: int):
        self._capacity = capacity
        self._buffer: List[T] = [None] * capacity  # type: ignore
        self._head = 0
        self._size = 0

    def add(self, item: T) -> None:
        """Add an item to the buffer. If the buffer is full, the oldest item will be evicted."""
        self._buffer[self._head] = item
        self._head = (self._head + 1) % self._capacity
        if self._size < self._capacity:
            self._size += 1

    def add_all(self, items: List[T]) -> None:
        """Add multiple items to the buffer at once."""
        for item in items:
            self.add(item)

    def get_recent(self, count: int) -> List[T]:
        """Get the most recent N items from the buffer.
        Returns fewer items if the buffer contains less than N items.
        """
        result: List[T] = []
        start = 0 if self._size < self._capacity else self._head
        available = min(count, self._size)

        for i in range(available):
            index = (start + self._size - available + i) % self._capacity
            result.append(self._buffer[index])  # type: ignore

        return result

    def to_array(self) -> List[T]:
        """Get all items currently in the buffer, in order from oldest to newest."""
        if self._size == 0:
            return []

        result: List[T] = []
        start = 0 if self._size < self._capacity else self._head

        for i in range(self._size):
            index = (start + i) % self._capacity
            result.append(self._buffer[index])  # type: ignore

        return result

    def clear(self) -> None:
        """Clear all items from the buffer."""
        self._head = 0
        self._size = 0

    def __len__(self) -> int:
        """Get the current number of items in the buffer."""
        return self._size