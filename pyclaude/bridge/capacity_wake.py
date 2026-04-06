"""Capacity wake for bridge."""

import asyncio
from typing import Optional, Callable


class CapacityWake:
    """Manages capacity waking for bridge connections."""

    def __init__(self):
        self._active = False
        self._wake_callback: Optional[Callable] = None

    async def wake(self) -> bool:
        """Wake up capacity."""
        if self._wake_callback:
            return await self._wake_callback()
        self._active = True
        return True

    async def sleep(self) -> None:
        """Put capacity to sleep."""
        self._active = False

    def is_active(self) -> bool:
        """Check if capacity is active."""
        return self._active

    def set_wake_callback(self, callback: Callable) -> None:
        """Set the wake callback."""
        self._wake_callback = callback


# Global capacity wake instance
_capacity_wake = CapacityWake()


def get_capacity_wake() -> CapacityWake:
    """Get the global capacity wake."""
    return _capacity_wake


__all__ = ['CapacityWake', 'get_capacity_wake']