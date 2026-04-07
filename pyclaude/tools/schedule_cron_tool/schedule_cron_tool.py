"""ScheduleCron tool."""
from typing import Any, Dict

class ScheduleCronTool:
    name = "schedule_cron"
    description = "Schedule cron tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['ScheduleCronTool']