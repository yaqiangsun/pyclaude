"""REPL tool."""
from typing import Any, Dict

class REPLTool:
    name = "repl"
    description = "REPL tool"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['REPLTool']