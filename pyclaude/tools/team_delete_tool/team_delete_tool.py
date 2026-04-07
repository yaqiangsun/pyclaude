"""TeamDelete tool."""
from typing import Any, Dict

class TeamDeleteTool:
    name = "team_delete"
    description = "Delete team"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['TeamDeleteTool']