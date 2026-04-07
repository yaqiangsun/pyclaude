# Glob Tool UI
# Reference: src/tools/GlobTool/UI.tsx (simplified)

from typing import Any, List
from dataclasses import dataclass


@dataclass
class GlobOutput:
    """Output from glob operation"""
    duration_ms: float
    num_files: int
    filenames: List[str]
    truncated: bool


def render_tool_use_message(pattern: str, path: str = None) -> str:
    """Render the tool use message"""
    location = f"matching '{pattern}'"
    if path:
        location += f" in {path}"
    return f"Glob: {location}"


def render_tool_result_message(output: GlobOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    lines = []

    if output.num_files == 0:
        lines.append("No files found")
    else:
        lines.append(f"Found {output.num_files} files ({output.duration_ms:.1f}ms)")
        lines.append("")
        lines.extend(output.filenames)

        if output.truncated:
            lines.append(f"\n... (truncated, showing first {len(output.filenames)})")

    return '\n'.join(lines)