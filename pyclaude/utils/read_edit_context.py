"""
Read/edit context utilities.

Context for read and edit operations.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ReadEditContext:
    """Context for read/edit operations."""
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: Optional[str] = None
    edit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_read_context(
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> ReadEditContext:
    """Create a read context.

    Args:
        file_path: File to read
        start_line: Start line number
        end_line: End line number

    Returns:
        Read context
    """
    return ReadEditContext(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
    )


def create_edit_context(
    file_path: str,
    content: Optional[str] = None,
) -> ReadEditContext:
    """Create an edit context.

    Args:
        file_path: File to edit
        content: New content

    Returns:
        Edit context
    """
    return ReadEditContext(
        file_path=file_path,
        content=content,
    )


__all__ = [
    "ReadEditContext",
    "create_read_context",
    "create_edit_context",
]