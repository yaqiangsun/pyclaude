# File Read Tool - Read files from the filesystem
# Reference: src/tools/FileReadTool/FileReadTool.ts

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .prompt import FILE_READ_TOOL_NAME, DESCRIPTION
from .limits import get_default_file_reading_limits
from .image_processor import (
    compress_image_buffer_with_token_limit,
    detect_image_format_from_buffer,
    maybe_resize_and_downsample_image_buffer,
)
import os


class FileReadInputSchema(BaseModel):
    """Input schema for FileReadTool"""
    file_path: str = Field(description="The path to the file to read")
    offset: Optional[int] = Field(
        default=1,
        description="The line number to start reading from"
    )
    limit: Optional[int] = Field(
        default=None,
        description="The number of lines to read"
    )


class FileReadOutputSchema(BaseModel):
    """Output schema for FileReadTool"""
    content: str = Field(description="The content of the file")
    file_path: str = Field(description="The path to the file that was read")
    total_lines: Optional[int] = Field(
        default=None,
        description="Total number of lines in the file"
    )
    truncated: bool = Field(
        default=False,
        description="Whether the output was truncated"
    )


class FileReadTool:
    """Tool for reading files from the filesystem"""

    name: str = FILE_READ_TOOL_NAME
    max_result_size_chars: int = 100_000
    should_defer: bool = True

    def __init__(self):
        self.limits = get_default_file_reading_limits()

    @property
    def input_schema(self) -> type[BaseModel]:
        return FileReadInputSchema

    @property
    def output_schema(self) -> type[BaseModel]:
        return FileReadOutputSchema

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the input parameters"""
        file_path = input_data.get("file_path")

        if not file_path:
            return {
                "result": False,
                "message": "Missing required parameter: file_path",
                "error_code": 1
            }

        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "result": False,
                "message": f"File not found: {file_path}",
                "error_code": 2
            }

        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return {
                "result": False,
                "message": f"Path is not a file: {file_path}",
                "error_code": 3
            }

        return {"result": True}

    async def description(self) -> str:
        return "Read a file from the filesystem"

    async def prompt(self) -> str:
        return DESCRIPTION

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'}
        ext = os.path.splitext(file_path)[1].lower()
        return ext in image_extensions

    def is_pdf_file(self, file_path: str) -> bool:
        """Check if file is a PDF"""
        return file_path.lower().endswith('.pdf')

    def is_notebook_file(self, file_path: str) -> bool:
        """Check if file is a Jupyter notebook"""
        return file_path.endswith('.ipynb')

    async def read_file(
        self,
        file_path: str,
        offset: int = 1,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read file content with optional range"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)

        # Convert 1-based offset to 0-based
        start = max(0, offset - 1)
        end = total_lines if limit is None else start + limit

        content = ''.join(lines[start:end])
        truncated = end < total_lines

        return {
            "content": content,
            "file_path": file_path,
            "total_lines": total_lines,
            "truncated": truncated
        }

    async def call(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the tool"""
        file_path = input_data.get("file_path")
        offset = input_data.get("offset", 1)
        limit = input_data.get("limit")

        if not file_path:
            raise ValueError("Missing required parameter: file_path")

        # Handle image files
        if self.is_image_file(file_path):
            return await self._read_image(file_path, context)

        # Handle PDF files
        if self.is_pdf_file(file_path):
            return await self._read_pdf(file_path, offset, limit)

        # Handle notebook files
        if self.is_notebook_file(file_path):
            return await self._read_notebook(file_path)

        # Regular file reading
        result = await self.read_file(file_path, offset, limit)

        return {"data": result}

    async def _read_image(
        self,
        file_path: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Read and process image file"""
        with open(file_path, 'rb') as f:
            buffer = f.read()

        # Detect format
        image_format = detect_image_format_from_buffer(buffer)

        # Resize if needed
        try:
            resized = maybe_resize_and_downsample_image_buffer(buffer)
            buffer = resized
        except Exception:
            pass  # Use original if resize fails

        import base64
        encoded = base64.b64encode(buffer).decode('utf-8')

        return {
            "data": {
                "content": f"[Image: {os.path.basename(file_path)}]",
                "file_path": file_path,
                "image_data": encoded,
                "image_format": image_format
            }
        }

    async def _read_pdf(
        self,
        file_path: str,
        offset: int,
        limit: Optional[int]
    ) -> Dict[str, Any]:
        """Read PDF file"""
        # Placeholder - would need PDF library
        return {
            "data": {
                "content": f"[PDF file: {file_path}]",
                "file_path": file_path,
                "total_pages": 0,
                "truncated": False
            }
        }

    async def _read_notebook(self, file_path: str) -> Dict[str, Any]:
        """Read Jupyter notebook"""
        import json
        with open(file_path, 'r') as f:
            notebook = json.load(f)

        cells = []
        for cell in notebook.get('cells', []):
            cell_type = cell.get('cell_type', 'code')
            source = ''.join(cell.get('source', []))
            cells.append({"type": cell_type, "source": source})

        return {
            "data": {
                "content": f"[Notebook: {file_path}]",
                "file_path": file_path,
                "cells": cells
            }
        }


# Export the tool instance
file_read_tool = FileReadTool()