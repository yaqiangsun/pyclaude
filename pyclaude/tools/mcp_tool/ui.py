# MCP Tool UI
# Reference: src/tools/MCPTool/UI.tsx (simplified)

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class MCPOutput:
    """Output from MCP operation"""
    success: bool
    results: Any
    error: Optional[str] = None


def render_tool_use_message(command: str, server_name: str = None, tool_name: str = None) -> str:
    """Render the tool use message"""
    parts = [f"MCP {command}"]
    if server_name:
        parts.append(f"@ {server_name}")
    if tool_name:
        parts.append(tool_name)
    return " ".join(parts)


def render_tool_result_message(output: MCPOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    if output.error:
        return f"Error: {output.error}"

    if not output.results:
        return "No results"

    import json
    return json.dumps(output.results, indent=2)