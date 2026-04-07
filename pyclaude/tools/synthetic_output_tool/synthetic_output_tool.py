"""SyntheticOutput tool."""
from typing import Any, Dict

class SyntheticOutputTool:
    name = "synthetic_output"
    description = "Synthetic output tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['SyntheticOutputTool']