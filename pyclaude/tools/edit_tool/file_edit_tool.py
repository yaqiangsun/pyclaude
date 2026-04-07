# File Edit Tool - Edit files in the filesystem
# Reference: src/tools/FileEditTool/FileEditTool.ts

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .constants import FILE_EDIT_TOOL_NAME, FILE_UNEXPECTEDLY_MODIFIED_ERROR
from .prompt import get_edit_tool_description
from .types import FileEditInput, FileEditOutput
from .utils import validate_edit_input, apply_edit
import os


class EditInputSchema(BaseModel):
    """Input schema for FileEditTool"""
    file_path: str = Field(description="The path to the file to edit")
    old_string: str = Field(description="The text to replace")
    new_string: str = Field(description="The replacement text")
    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences of old_string"
    )


class EditOutputSchema(BaseModel):
    """Output schema for FileEditTool"""
    message: str = Field(description="Status message")
    file_path: str = Field(description="The file that was edited")
    operations: List[Dict[str, Any]] = Field(
        description="List of edit operations performed"
    )


class FileEditTool:
    """Tool for editing files in the filesystem"""

    name: str = FILE_EDIT_TOOL_NAME
    max_result_size_chars: int = 100_000
    should_defer: bool = True

    def __init__(self):
        pass

    @property
    def input_schema(self) -> type[BaseModel]:
        return EditInputSchema

    @property
    def output_schema(self) -> type[BaseModel]:
        return EditOutputSchema

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the input parameters"""
        return validate_edit_input(input_data, context)

    async def description(self) -> str:
        return get_edit_tool_description()

    async def call(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the tool"""
        return await apply_edit(input_data, context)


# Export the tool instance
file_edit_tool = FileEditTool()