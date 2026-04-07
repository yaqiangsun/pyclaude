"""TaskGet tool."""
from typing import Any, Dict

class TaskGetTool:
    name = "task_get"
    description = "Get task"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['TaskGetTool']