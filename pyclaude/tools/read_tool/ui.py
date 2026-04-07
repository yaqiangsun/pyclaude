# File Read Tool UI
# Reference: src/tools/FileReadTool/UI.tsx (simplified)

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class FileReadOutput:
    """Output from file read operation"""
    content: str
    file_path: str
    total_lines: Optional[int] = None
    truncated: bool = False


def render_tool_use_message(file_path: str, offset: Optional[int] = None, limit: Optional[int] = None) -> str:
    """Render the tool use message"""
    location = f"{file_path}"
    if offset or limit:
        parts = []
        if offset:
            parts.append(f"line {offset}")
        if limit:
            parts.append(f"{limit} lines")
        location += f" ({', '.join(parts)})"
    return f"Read: {location}"


def render_tool_result_message(
    output: FileReadOutput,
    verbose: bool = False
) -> str:
    """Render the tool result message"""
    lines = []

    # Add file path header
    lines.append(f"=== {output.file_path} ===")

    if output.total_lines:
        lines.append(f"({output.total_lines} lines)")

    # Add content
    lines.append("")
    lines.append(output.content)

    if output.truncated:
        lines.append(f"\n... (truncated)")

    return '\n'.join(lines)