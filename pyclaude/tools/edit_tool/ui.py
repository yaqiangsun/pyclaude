# File Edit Tool UI
# Reference: src/tools/FileEditTool/UI.tsx (simplified)

from typing import Any, List, Optional
from dataclasses import dataclass


@dataclass
class EditOutput:
    """Output from file edit operation"""
    message: str
    file_path: str
    operations: List[Dict[str, Any]]


def render_tool_use_message(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False
) -> str:
    """Render the tool use message"""
    action = "Replace" if not replace_all else "Replace all"
    return f"{action} in {file_path}"


def render_tool_result_message(
    output: EditOutput,
    verbose: bool = False
) -> str:
    """Render the tool result message"""
    lines = [output.message]

    if verbose and output.operations:
        lines.append("\nOperations:")
        for op in output.operations:
            lines.append(f"  - {op.get('type', 'edit')}: {op.get('description', '')}")

    return '\n'.join(lines)