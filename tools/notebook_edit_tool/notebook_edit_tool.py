# Notebook Edit Tool - Edit Jupyter notebooks
# Reference: src/tools/NotebookEditTool/NotebookEditTool.ts

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
import os


NOTEBOOK_EDIT_TOOL_NAME = "NotebookEdit"

DESCRIPTION = """- Use this tool to edit Jupyter notebooks (.ipynb files)
- Supports adding, modifying, and removing cells
- Preserves notebook metadata and output"""


@dataclass
class CellEdit:
    """Edit to apply to a cell"""
    cell_index: int
    cell_type: str  # "code" or "markdown"
    source: str


@dataclass
class NotebookEditInput:
    """Input schema for NotebookEditTool"""
    file_path: str
    edits: List[CellEdit]


@dataclass
class NotebookEditOutput:
    """Output schema for NotebookEditTool"""
    message: str
    file_path: str
    cells_modified: int


class NotebookEditTool:
    """Tool for editing Jupyter notebooks"""

    name: str = NOTEBOOK_EDIT_TOOL_NAME
    description: str = DESCRIPTION
    should_defer: bool = True

    def __init__(self):
        pass

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate input parameters"""
        file_path = input_data.get("file_path")
        edits = input_data.get("edits")

        if not file_path:
            return {
                "result": False,
                "message": "Missing required parameter: file_path",
                "error_code": 1
            }

        if not os.path.exists(file_path):
            return {
                "result": False,
                "message": f"File not found: {file_path}",
                "error_code": 2
            }

        return {"result": True}

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute notebook edit"""
        file_path = input_data.get("file_path")
        edits = input_data.get("edits", [])

        if not file_path:
            return {"success": False, "error": "Missing file_path parameter"}

        # Load notebook
        with open(file_path, 'r') as f:
            notebook = json.load(f)

        # Apply edits
        cells = notebook.get('cells', [])
        for edit in edits:
            cell_index = edit.get('cell_index', 0)
            cell_type = edit.get('cell_type', 'code')
            source = edit.get('source', '')

            if cell_index < len(cells):
                cells[cell_index]['cell_type'] = cell_type
                cells[cell_index]['source'] = [source] if isinstance(source, str) else source
            else:
                # Add new cell
                cells.append({
                    'cell_type': cell_type,
                    'source': [source] if isinstance(source, str) else source,
                    'outputs': [],
                    'metadata': {}
                })

        notebook['cells'] = cells

        # Save notebook
        with open(file_path, 'w') as f:
            json.dump(notebook, f, indent=2)

        return {
            "success": True,
            "message": f"Edited {file_path}",
            "file_path": file_path,
            "cells_modified": len(edits)
        }


notebook_edit_tool = NotebookEditTool()