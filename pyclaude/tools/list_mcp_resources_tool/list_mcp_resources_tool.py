"""ListMcpResources tool."""
from typing import Any, Dict

class ListMcpResourcesTool:
    name = "list_mcp_resources"
    description = "List MCP resources"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['ListMcpResourcesTool']