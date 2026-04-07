"""
GrepTool - Search files for content.
"""

from typing import Any, Dict, List, Optional, Callable
import os
import re
import time
from dataclasses import dataclass


GREP_TOOL_NAME = "Grep"

DESCRIPTION = """- A powerful search tool built on ripgrep
- Supports full regex syntax (e.g., "log.*Error", "function\\s+\\w+")
- Filter files with glob parameter (e.g. "*.js", "*.{ts,tsx}")
- Use this when you need to find code or text within files"""


@dataclass
class GrepToolInput:
    """Input schema for GrepTool."""
    pattern: str
    path: Optional[str] = None
    glob: Optional[str] = None
    output_mode: str = "content"  # "content", "files_with_matches", "count"


@dataclass
class GrepToolOutput:
    """Output schema for GrepTool."""
    duration_ms: float
    results: List[str]
    count: int


MAX_RESULTS = 100


def search_files(
    pattern: str,
    path: Optional[str] = None,
    glob: Optional[str] = None,
    output_mode: str = "content",
) -> List[str]:
    """Search files for a pattern."""
    search_dir = path or os.getcwd()
    results: List[str] = []

    try:
        regex = re.compile(pattern)
    except re.error:
        return [f"Invalid regex pattern: {pattern}"]

    # Walk through directory
    for root, dirs, files in os.walk(search_dir):
        # Filter by glob if provided
        if glob:
            import fnmatch
            files = [f for f in files if fnmatch.fnmatch(f, glob)]

        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            if output_mode == "content":
                                results.append(f"{filepath}:{line_num}:{line.rstrip()}")
                            elif output_mode == "count":
                                results.append(f"{filepath}")
                                break
                            elif output_mode == "files_with_matches":
                                if filepath not in results:
                                    results.append(filepath)
                                    break

                if len(results) >= MAX_RESULTS and output_mode == "content":
                    break
            except (IOError, OSError):
                continue

        if len(results) >= MAX_RESULTS and output_mode == "content":
            break

    if output_mode == "count":
        results = [str(len(set(results)))]

    return results[:MAX_RESULTS]


async def execute_grep(
    input_dict: Dict[str, Any],
    get_app_state: Callable,
    set_app_state: Callable,
    abort_controller: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute the Grep tool."""
    start_time = time.time()

    try:
        pattern = input_dict.get("pattern", "")
        path = input_dict.get("path")
        glob = input_dict.get("glob")
        output_mode = input_dict.get("output_mode", "content")

        if not pattern:
            return {
                "success": False,
                "error": "Pattern is required",
            }

        # Execute search
        results = search_files(pattern, path, glob, output_mode)

        duration_ms = (time.time() - start_time) * 1000

        return {
            "success": True,
            "durationMs": duration_ms,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "GREP_TOOL_NAME",
    "DESCRIPTION",
    "GrepToolInput",
    "GrepToolOutput",
    "execute_grep",
]