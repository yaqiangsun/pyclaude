"""
Generated files utilities.

Track generated files.
"""

import os
from typing import Set, List


class GeneratedFilesTracker:
    """Track generated files."""

    def __init__(self):
        self._files: Set[str] = set()

    def add(self, path: str) -> None:
        """Add generated file.

        Args:
            path: File path
        """
        self._files.add(os.path.abspath(path))

    def remove(self, path: str) -> None:
        """Remove generated file.

        Args:
            path: File path
        """
        self._files.discard(os.path.abspath(path))

    def is_generated(self, path: str) -> bool:
        """Check if file was generated.

        Args:
            path: File path

        Returns:
            True if generated
        """
        return os.path.abspath(path) in self._files

    def get_all(self) -> List[str]:
        """Get all generated files.

        Returns:
            List of file paths
        """
        return list(self._files)


# Global tracker
_tracker = GeneratedFilesTracker()


def get_generated_tracker() -> GeneratedFilesTracker:
    """Get global generated files tracker."""
    return _tracker


__all__ = [
    "GeneratedFilesTracker",
    "get_generated_tracker",
]