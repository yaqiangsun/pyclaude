"""
JetBrains utilities.

JetBrains IDE integration.
"""

import os
import subprocess
from typing import Optional, List


def find_jetbrains_ides() -> List[str]:
    """Find installed JetBrains IDEs.

    Returns:
        List of IDE paths
    """
    # Common JetBrains paths on macOS
    paths = [
        "/Applications/IntelliJ IDEA.app",
        "/Applications/WebStorm.app",
        "/Applications/PyCharm.app",
        "/Applications/GoLand.app",
        "/Applications/CLion.app",
    ]

    return [p for p in paths if os.path.exists(p)]


def get_jetbrains_toolbox_path() -> Optional[str]:
    """Get JetBrains Toolbox path.

    Returns:
        Toolbox path or None
    """
    toolbox = os.path.expanduser("~/Library/Application Support/JetBrains/Toolbox")
    if os.path.exists(toolbox):
        return toolbox
    return None


def open_in_jetbrains(path: str, ide: str) -> bool:
    """Open file in JetBrains IDE.

    Args:
        path: File path
        ide: IDE name

    Returns:
        True if successful
    """
    # Placeholder implementation
    return False


__all__ = [
    "find_jetbrains_ides",
    "get_jetbrains_toolbox_path",
    "open_in_jetbrains",
]