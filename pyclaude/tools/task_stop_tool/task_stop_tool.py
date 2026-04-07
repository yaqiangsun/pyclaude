"""TaskStop tool."""
from typing import Any, Dict

class TaskStopTool:
    name = "task_stop"
    description = "Stop task"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['TaskStopTool']