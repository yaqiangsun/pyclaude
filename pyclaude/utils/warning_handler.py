"""
Warning handler utilities.

Manage and suppress warnings.
"""

import warnings
import logging
from typing import Optional, Callable, Any


class WarningHandler:
    """Handle and filter warnings."""

    def __init__(self):
        self.suppressed: set = set()
        self._original_filters = warnings.filters.copy()

    def suppress(self, warning_type: type) -> None:
        """Suppress a warning type.

        Args:
            warning_type: Warning class
        """
        self.suppressed.add(warning_type)
        warnings.filterwarnings("ignore", category=warning_type)

    def restore(self) -> None:
        """Restore original warning filters."""
        warnings.filters[:] = self._original_filters


def warn_once(message: str, category: type = UserWarning) -> None:
    """Warn once per message.

    Args:
        message: Warning message
        category: Warning category
    """
    if not hasattr(warn_once, "_seen"):
        warn_once._seen = set()

    if message not in warn_once._seen:
        warn_once._seen.add(message)
        warnings.warn(message, category)


__all__ = [
    "WarningHandler",
    "warn_once",
]