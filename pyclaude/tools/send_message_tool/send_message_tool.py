"""SendMessage tool."""
from typing import Any, Dict

class SendMessageTool:
    name = "send_message"
    description = "Send message tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['SendMessageTool']