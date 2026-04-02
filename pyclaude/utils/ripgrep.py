"""
Ripgrep utilities.

Wrapper for ripgrep search.
"""

import subprocess
from typing import List, Optional, Dict, Any


async def run_ripgrep(
    pattern: str,
    path: str,
    options: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Run ripgrep search.

    Args:
        pattern: Search pattern
        path: Path to search
        options: Ripgrep options

    Returns:
        List of matching lines
    """
    args = ["rg", "--line-number", pattern, path]
    if options:
        if options.get("ignore_case"):
            args.append("-i")
        if options.get("whole_word"):
            args.append("-w")
        if options.get("regex"):
            args.append("-F")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=options.get("timeout", 30) if options else 30,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
    except Exception:
        pass
    return []


def count_files_rounded_rg(path: str, abort_signal: Optional[Any] = None) -> int:
    """Count files in directory using ripgrep.

    Args:
        path: Path to count
        abort_signal: Optional abort signal

    Returns:
        File count (rounded)
    """
    # Placeholder - would use ripgrep to count files
    return 0


__all__ = [
    "run_ripgrep",
    "count_files_rounded_rg",
]