# Notebook Edit Tool UI
# Reference: src/tools/NotebookEditTool/UI.tsx (simplified)

from typing import Any, List
from dataclasses import dataclass


@dataclass
class NotebookEditOutput:
    """Output from notebook edit operation"""
    message: str
    file_path: str
    cells_modified: int


def render_tool_use_message(file_path: str, num_edits: int = None) -> str:
    """Render the tool use message"""
    parts = [f"Notebook Edit: {file_path}"]
    if num_edits:
        parts.append(f"({num_edits} edits)")
    return " ".join(parts)


def render_tool_result_message(output: NotebookEditOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    lines = [output.message]
    lines.append(f"Cells modified: {output.cells_modified}")
    return '\n'.join(lines)