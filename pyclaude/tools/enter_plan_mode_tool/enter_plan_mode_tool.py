"""EnterPlanMode tool."""
from typing import Any, Dict

class EnterPlanModeTool:
    name = "enter_plan_mode"
    description = "Enter plan mode"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['EnterPlanModeTool']