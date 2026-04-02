"""
Paste store utilities.

Clipboard paste storage.
"""

import os
import json
from typing import Optional, List


class PasteStore:
    """Store for clipboard pastes."""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self._items: List[str] = []

    def add(self, text: str) -> None:
        """Add paste to store.

        Args:
            text: Paste text
        """
        if text in self._items:
            self._items.remove(text)
        self._items.insert(0, text)
        if len(self._items) > self.max_items:
            self._items = self._items[:self.max_items]

    def get_recent(self, count: int = 10) -> List[str]:
        """Get recent pastes.

        Args:
            count: Number of items

        Returns:
            List of pastes
        """
        return self._items[:count]

    def clear(self) -> None:
        """Clear all pastes."""
        self._items.clear()


# Global paste store
_paste_store = PasteStore()


def get_paste_store() -> PasteStore:
    """Get global paste store."""
    return _paste_store


__all__ = [
    "PasteStore",
    "get_paste_store",
]