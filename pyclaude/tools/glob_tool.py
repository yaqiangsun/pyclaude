"""
GlobTool - Fast file pattern matching tool.
"""

from typing import Any, Dict, List, Optional, Callable
import os
import time
from dataclasses import dataclass

from ..utils.cwd import get_cwd
from ..utils.errors import is_enoent


GLOB_TOOL_NAME = "Glob"

DESCRIPTION = """- Fast file pattern matching tool that works with any codebase size
- Supports glob patterns like "**/*.js" or "src/**/*.ts"
- Returns matching file paths sorted by modification time
- Use this tool when you need to find files by name patterns
- When you are doing an open ended search that may require multiple rounds of globbing and grepping, use the Agent tool instead"""


@dataclass
class GlobToolInput:
    """Input schema for GlobTool."""
    pattern: str
    path: Optional[str] = None


@dataclass
class GlobToolOutput:
    """Output schema for GlobTool."""
    duration_ms: float
    num_files: int
    filenames: List[str]
    truncated: bool


MAX_RESULTS = 100


def glob_pattern(pattern: str, path: Optional[str] = None) -> List[str]:
    """Match files against a glob pattern."""
    import fnmatch

    search_dir = path or get_cwd()
    results: List[str] = []

    # Simple glob implementation
    # For a full implementation, would use pathlib or glob.glob
    for root, dirs, files in os.walk(search_dir):
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                full_path = os.path.join(root, filename)
                results.append(full_path)

    # Sort by modification time (newest first)
    results.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return results


async def execute_glob(
    input_dict: Dict[str, Any],
    get_app_state: Callable,
    set_app_state: Callable,
    abort_controller: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute the Glob tool."""
    start_time = time.time()

    try:
        pattern = input_dict.get("pattern", "")
        path = input_dict.get("path")

        if not pattern:
            return {
                "success": False,
                "error": "Pattern is required",
            }

        # Execute glob
        filenames = glob_pattern(pattern, path)

        # Truncate if needed
        truncated = len(filenames) > MAX_RESULTS
        if truncated:
            filenames = filenames[:MAX_RESULTS]

        duration_ms = (time.time() - start_time) * 1000

        return {
            "success": True,
            "durationMs": duration_ms,
            "numFiles": len(filenames),
            "filenames": filenames,
            "truncated": truncated,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "GLOB_TOOL_NAME",
    "DESCRIPTION",
    "GlobToolInput",
    "GlobToolOutput",
    "execute_glob",
]