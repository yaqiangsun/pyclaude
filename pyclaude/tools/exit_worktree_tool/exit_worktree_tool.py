"""ExitWorktree tool."""
from typing import Any, Dict

class ExitWorktreeTool:
    name = "exit_worktree"
    description = "Exit worktree"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['ExitWorktreeTool']