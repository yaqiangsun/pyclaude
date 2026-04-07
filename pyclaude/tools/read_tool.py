"""
ReadTool - Read files from the filesystem.
"""

from typing import Any, Dict, List, Optional, Callable
import os
from dataclasses import dataclass

from . import BaseTool


READ_TOOL_NAME = "Read"

DESCRIPTION = """- Use this tool to read files from the local filesystem
- Returns the contents of the file
- Can specify line range with offset and limit parameters"""

MAX_CHARS = 100000


@dataclass
class ReadToolInput:
    """Input for ReadTool."""
    file_path: str
    offset: Optional[int] = None
    limit: Optional[int] = None


@dataclass
class ReadToolOutput:
    """Output from ReadTool."""
    content: str = ""
    lines: int = 0
    truncated: bool = False
    error: str = ""
    success: bool = True


class ReadTool(BaseTool):
    """Tool for reading files."""

    def __init__(self):
        super().__init__(READ_TOOL_NAME, DESCRIPTION)
        self.input_schema = {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read",
                },
                "offset": {
                    "type": "number",
                    "description": "Line offset to start reading from",
                },
                "limit": {
                    "type": "number",
                    "description": "Number of lines to read",
                },
            },
            "required": ["file_path"],
        }

    async def execute(
        self,
        input_dict: Dict[str, Any],
        get_app_state: Callable,
        set_app_state: Callable,
        abort_controller: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute the Read tool."""
        try:
            file_path = input_dict.get("file_path", "")
            offset = input_dict.get("offset")
            limit = input_dict.get("limit")

            if not file_path:
                return {
                    "success": False,
                    "error": "file_path is required",
                }

            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                }

            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": f"Not a file: {file_path}",
                }

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.split('\n')

            # Apply offset and limit
            if offset is not None:
                lines = lines[offset:]
            if limit is not None:
                lines = lines[:limit]

            content = '\n'.join(lines)
            truncated = len(content) > MAX_CHARS
            if truncated:
                content = content[:MAX_CHARS]

            return {
                "success": True,
                "content": content,
                "lines": len(lines),
                "truncated": truncated,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


async def execute_read(
    input_dict: Dict[str, Any],
    get_app_state: Callable,
    set_app_state: Callable,
    abort_controller: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute read operation using ReadTool."""
    tool = ReadTool()
    return await tool.execute(input_dict, get_app_state, set_app_state, abort_controller)


__all__ = ['ReadTool', 'ReadToolInput', 'ReadToolOutput', 'execute_read', 'READ_TOOL_NAME', 'DESCRIPTION', 'MAX_CHARS']