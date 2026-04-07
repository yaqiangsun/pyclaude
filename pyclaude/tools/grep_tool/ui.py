# Grep Tool UI
# Reference: src/tools/GrepTool/UI.tsx (simplified)

from typing import Any, List
from dataclasses import dataclass


@dataclass
class GrepOutput:
    """Output from grep operation"""
    duration_ms: float
    results: List[str]
    count: int


def render_tool_use_message(
    pattern: str,
    path: str = None,
    glob: str = None
) -> str:
    """Render the tool use message"""
    location = f"'{pattern}'"
    if glob:
        location += f" (glob: {glob})"
    if path:
        location += f" in {path}"
    return f"Grep: {location}"


def render_tool_result_message(output: GrepOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    lines = []

    lines.append(f"Found {output.count} matches ({output.duration_ms:.1f}ms)")
    lines.append("")

    if output.results:
        lines.extend(output.results)
    else:
        lines.append("No matches found")

    return '\n'.join(lines)