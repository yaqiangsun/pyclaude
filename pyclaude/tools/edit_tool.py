"""
EditTool - Edit files in the filesystem.
"""

from typing import Any, Dict, Optional, Callable
import os
import re
import time
from dataclasses import dataclass


EDIT_TOOL_NAME = "Edit"

DESCRIPTION = """- Use this tool to make exact string replacements in files
- The edit will fail if old_string is not unique in the file
- Use replace_all to change every instance of old_string"""


@dataclass
class EditToolInput:
    """Input schema for EditTool."""
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False


async def execute_edit(
    input_dict: Dict[str, Any],
    get_app_state: Callable,
    set_app_state: Callable,
    abort_controller: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute the Edit tool."""
    try:
        file_path = input_dict.get("file_path", "")
        old_string = input_dict.get("old_string", "")
        new_string = input_dict.get("new_string", "")
        replace_all = input_dict.get("replace_all", False)

        if not file_path:
            return {
                "success": False,
                "error": "file_path is required",
            }

        if not old_string:
            return {
                "success": False,
                "error": "old_string is required",
            }

        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check if old_string exists
        if old_string not in content:
            return {
                "success": False,
                "error": f"old_string not found in file: {file_path}",
            }

        # Replace
        if replace_all:
            new_content = content.replace(old_string, new_string)
        else:
            new_content = content.replace(old_string, new_string, 1)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {
            "success": True,
            "message": "File edited successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


__all__ = [
    "EDIT_TOOL_NAME",
    "DESCRIPTION",
    "EditToolInput",
    "execute_edit",
]