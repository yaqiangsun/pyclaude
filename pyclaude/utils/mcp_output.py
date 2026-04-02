"""
MCP output storage utilities.

MCP tool output storage.
"""

import json
import os
from typing import Optional, Dict, Any


def get_mcp_output_path(session_id: str) -> str:
    """Get MCP output storage path.

    Args:
        session_id: Session ID

    Returns:
        Storage path
    """
    cache_dir = os.environ.get("CLAUDE_CODE_CACHE_DIR", "/tmp/claude-cache")
    return os.path.join(cache_dir, "mcp", f"{session_id}.jsonl")


def store_mcp_output(
    session_id: str,
    tool_name: str,
    output: Any,
) -> bool:
    """Store MCP tool output.

    Args:
        session_id: Session ID
        tool_name: Tool name
        output: Tool output

    Returns:
        True if successful
    """
    try:
        path = get_mcp_output_path(session_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "a") as f:
            f.write(json.dumps({
                "tool": tool_name,
                "output": output,
            }) + "\n")
        return True
    except Exception:
        return False


def load_mcp_outputs(session_id: str) -> list:
    """Load MCP tool outputs.

    Args:
        session_id: Session ID

    Returns:
        List of outputs
    """
    try:
        path = get_mcp_output_path(session_id)
        if not os.path.exists(path):
            return []

        outputs = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    outputs.append(json.loads(line))
        return outputs
    except Exception:
        return []


__all__ = [
    "get_mcp_output_path",
    "store_mcp_output",
    "load_mcp_outputs",
]