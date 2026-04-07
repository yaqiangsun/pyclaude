"""TaskList tool."""
from typing import Any, Dict

class TaskListTool:
    name = "task_list"
    description = "List tasks"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['TaskListTool']