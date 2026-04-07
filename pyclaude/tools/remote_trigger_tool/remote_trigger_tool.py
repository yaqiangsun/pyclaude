"""RemoteTrigger tool."""
from typing import Any, Dict

class RemoteTriggerTool:
    name = "remote_trigger"
    description = "Remote trigger tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['RemoteTriggerTool']