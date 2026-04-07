"""Sleep tool."""
from typing import Any, Dict

class SleepTool:
    name = "sleep"
    description = "Sleep tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['SleepTool']