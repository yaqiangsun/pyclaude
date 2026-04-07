"""MCP tool."""
from typing import Any, Dict

class MCPTool:
    name = "mcp"
    description = "MCP tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['MCPTool']