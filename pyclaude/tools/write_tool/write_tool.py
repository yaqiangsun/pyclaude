# File Write Tool - Write content to files
# Reference: src/tools/FileWriteTool/FileWriteTool.ts

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
import os


FILE_WRITE_TOOL_NAME = "Write"

DESCRIPTION = """- Use this tool to write files to the local filesystem
- This tool will overwrite existing files if they exist
- Provide the absolute path to the file"""


@dataclass
class WriteInputSchema:
    """Input schema for FileWriteTool"""
    file_path: str
    content: str


@dataclass
class WriteOutputSchema:
    """Output schema for FileWriteTool"""
    message: str
    file_path: str
    bytes_written: int


class FileWriteTool:
    """Tool for writing content to files"""

    name: str = FILE_WRITE_TOOL_NAME
    max_result_size_chars: int = 100_000
    should_defer: bool = True

    def __init__(self):
        pass

    @property
    def input_schema(self):
        return WriteInputSchema

    @property
    def output_schema(self):
        return WriteOutputSchema

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the input parameters"""
        file_path = input_data.get("file_path")
        content = input_data.get("content")

        if not file_path:
            return {
                "result": False,
                "message": "Missing required parameter: file_path",
                "error_code": 1
            }

        if content is None:
            return {
                "result": False,
                "message": "Missing required parameter: content",
                "error_code": 2
            }

        return {"result": True}

    async def description(self) -> str:
        return DESCRIPTION

    async def call(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the tool"""
        file_path = input_data.get("file_path")
        content = input_data.get("content")

        if not file_path or content is None:
            raise ValueError("Missing required parameters")

        # Ensure directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        bytes_written = len(content.encode('utf-8'))

        return {
            "data": {
                "message": f"Successfully wrote to {file_path}",
                "file_path": file_path,
                "bytes_written": bytes_written
            }
        }


# Export the tool instance
file_write_tool = FileWriteTool()