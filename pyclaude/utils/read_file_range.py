"""
Read file range utilities.

Read specific line ranges from files.
"""

import os
from typing import Optional, Tuple


def read_file_range(
    file_path: str,
    start_line: int,
    end_line: Optional[int] = None,
) -> str:
    """Read a range of lines from a file.

    Args:
        file_path: Path to file
        start_line: Start line (1-indexed)
        end_line: End line (inclusive, optional)

    Returns:
        Selected lines
    """
    if end_line is None:
        end_line = start_line

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            return ''.join(lines[start_idx:end_idx])
    except Exception:
        return ""


def read_file_lines(
    file_path: str,
    line_numbers: Optional[Tuple[int, int]] = None,
) -> list:
    """Read specific lines from file.

    Args:
        file_path: Path to file
        line_numbers: (start, end) tuple

    Returns:
        List of lines
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if line_numbers:
                start, end = line_numbers
                return lines[start-1:end]
            return lines
    except Exception:
        return []


__all__ = [
    "read_file_range",
    "read_file_lines",
]