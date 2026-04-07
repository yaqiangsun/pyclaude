# LSP Tool UI
# Reference: src/tools/LSPTool/UI.tsx (simplified)

from typing import Any, List
from dataclasses import dataclass


@dataclass
class LSPOutput:
    """Output from LSP operation"""
    results: List[Any]
    error: Optional[str] = None


def render_tool_use_message(command: str, file_path: str, line: int = None) -> str:
    """Render the tool use message"""
    location = file_path
    if line:
        location += f":{line}"
    return f"LSP {command}: {location}"


def render_tool_result_message(output: LSPOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    if output.error:
        return f"Error: {output.error}"

    if not output.results:
        return "No results"

    lines = [f"Found {len(output.results)} results:"]
    for result in output.results:
        lines.append(f"  - {result}")

    return '\n'.join(lines)