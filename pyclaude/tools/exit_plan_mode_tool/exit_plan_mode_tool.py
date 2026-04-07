"""ExitPlanMode tool."""
from typing import Any, Dict

class ExitPlanModeTool:
    name = "exit_plan_mode"
    description = "Exit plan mode"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['ExitPlanModeTool']