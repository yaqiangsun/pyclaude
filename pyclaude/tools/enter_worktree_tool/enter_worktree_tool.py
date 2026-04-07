"""EnterWorktree tool."""
from typing import Any, Dict

class EnterWorktreeTool:
    name = "enter_worktree"
    description = "Enter worktree"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['EnterWorktreeTool']