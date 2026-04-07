"""ReadMcpResource tool."""
from typing import Any, Dict

class ReadMcpResourceTool:
    name = "read_mcp_resource"
    description = "Read MCP resource"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['ReadMcpResourceTool']