"""
WriteTool - Write files to the filesystem.
"""

from typing import Any, Dict, Optional, Callable
import os
from dataclasses import dataclass


WRITE_TOOL_NAME = "Write"

DESCRIPTION = """- Use this tool to write files to the local filesystem
- This tool will overwrite existing files if they exist
- Provide the absolute path to the file"""


@dataclass
class WriteToolInput:
    """Input schema for WriteTool."""
    file_path: str
    content: str


async def execute_write(
    input_dict: Dict[str, Any],
    get_app_state: Callable,
    set_app_state: Callable,
    abort_controller: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute the Write tool."""
    try:
        file_path = input_dict.get("file_path", "")
        content = input_dict.get("content", "")

        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
            }

        # Create parent directories if needed
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "message": f"File written to {file_path}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "WRITE_TOOL_NAME",
    "DESCRIPTION",
    "WriteToolInput",
    "execute_write",
]