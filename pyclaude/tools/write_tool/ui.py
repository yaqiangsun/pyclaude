# File Write Tool UI
# Reference: src/tools/FileWriteTool/UI.tsx (simplified)

from typing import Any
from dataclasses import dataclass


@dataclass
class WriteOutput:
    """Output from file write operation"""
    message: str
    file_path: str
    bytes_written: int


def render_tool_use_message(file_path: str) -> str:
    """Render the tool use message"""
    return f"Write: {file_path}"


def render_tool_result_message(output: WriteOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    lines = [output.message]

    if verbose:
        lines.append(f"Bytes written: {output.bytes_written}")

    return '\n'.join(lines)