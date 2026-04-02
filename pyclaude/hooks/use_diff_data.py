"""
Use diff data hook.

Hook to fetch current git diff data on demand.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

MAX_LINES_PER_FILE = 400


@dataclass
class DiffFile:
    """Diff file information."""
    path: str
    lines_added: int
    lines_removed: int
    is_binary: bool
    is_large_file: bool
    is_truncated: bool
    is_new_file: bool = False
    is_untracked: bool = False


@dataclass
class DiffData:
    """Diff data result."""
    stats: Optional[Dict[str, Any]]
    files: List[DiffFile]
    hunks: Dict[str, List[Dict[str, Any]]]
    loading: bool


# Placeholder for git diff functions
async def fetch_git_diff() -> Optional[Dict[str, Any]]:
    """Fetch git diff stats."""
    # Placeholder implementation
    return None


async def fetch_git_diff_hunks() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch git diff hunks."""
    # Placeholder implementation
    return {}


class DiffDataFetcher:
    """Fetches diff data on demand."""

    def __init__(self):
        self._diff_result: Optional[Dict[str, Any]] = None
        self._hunks: Dict[str, List[Dict[str, Any]]] = {}
        self._loading = True
        self._cancelled = False

    async def fetch(self) -> DiffData:
        """Fetch diff data."""
        self._cancelled = False

        try:
            # Fetch both stats and hunks
            stats_result, hunks_result = await asyncio.gather(
                fetch_git_diff(),
                fetch_git_diff_hunks(),
            )

            if not self._cancelled:
                self._diff_result = stats_result
                self._hunks = hunks_result
                self._loading = False
        except Exception:
            if not self._cancelled:
                self._diff_result = None
                self._hunks = {}
                self._loading = False

        return self._build_result()

    def cancel(self) -> None:
        """Cancel the fetch operation."""
        self._cancelled = True

    def _build_result(self) -> DiffData:
        """Build the diff result."""
        if not self._diff_result:
            return DiffData(stats=None, files=[], hunks={}, loading=self._loading)

        stats = self._diff_result.get("stats")
        per_file_stats = self._diff_result.get("perFileStats", {})

        files: List[DiffFile] = []

        for path, file_stats in per_file_stats.items():
            file_hunks = self._hunks.get(path, [])
            is_untracked = file_stats.get("isUntracked", False)

            # Detect large file
            is_large_file = (
                not file_stats.get("isBinary", False) and
                not is_untracked and
                not file_hunks
            )

            # Detect truncated file
            total_lines = file_stats.get("added", 0) + file_stats.get("removed", 0)
            is_truncated = (
                not is_large_file and
                not file_stats.get("isBinary", False) and
                total_lines > MAX_LINES_PER_FILE
            )

            files.append(DiffFile(
                path=path,
                lines_added=file_stats.get("added", 0),
                lines_removed=file_stats.get("removed", 0),
                is_binary=file_stats.get("isBinary", False),
                is_large_file=is_large_file,
                is_truncated=is_truncated,
                is_untracked=is_untracked,
            ))

        # Sort files by path
        files.sort(key=lambda f: f.path)

        return DiffData(stats=stats, files=files, hunks=self._hunks, loading=False)


# Global instance
_diff_fetcher = DiffDataFetcher()


async def use_diff_data() -> DiffData:
    """Hook to fetch current git diff data on demand.

    Returns:
        DiffData with stats, files, and hunks
    """
    return await _diff_fetcher.fetch()


__all__ = [
    "DiffFile",
    "DiffData",
    "DiffDataFetcher",
    "use_diff_data",
]