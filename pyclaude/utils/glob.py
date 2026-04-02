"""
Glob utilities.

File globbing helpers.
"""

import os
import fnmatch
from typing import List, Optional
from pathlib import Path


def glob_match(path: str, patterns: List[str]) -> bool:
    """Check if path matches any pattern.

    Args:
        path: File path
        patterns: List of glob patterns

    Returns:
        True if matches
    """
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def find_matching(
    root: str,
    patterns: List[str],
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """Find files matching patterns.

    Args:
        root: Root directory
        patterns: Glob patterns
        exclude: Exclude patterns

    Returns:
        List of matching paths
    """
    matches = []
    exclude = exclude or []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter directories
        dirnames[:] = [d for d in dirnames if not glob_match(d, exclude)]

        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if glob_match(path, patterns) and not glob_match(path, exclude):
                matches.append(path)

    return matches


def expand_glob(pattern: str) -> List[str]:
    """Expand glob pattern to files.

    Args:
        pattern: Glob pattern

    Returns:
        List of matching paths
    """
    import glob as stdlib_glob
    return stdlib_glob.glob(pattern, recursive=True)


__all__ = [
    "glob_match",
    "find_matching",
    "expand_glob",
]