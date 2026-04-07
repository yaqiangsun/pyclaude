"""WebSearch tool."""
from typing import Any, Dict

class WebSearchTool:
    name = "web_search"
    description = "Web search tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['WebSearchTool']