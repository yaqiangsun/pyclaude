"""AskUserQuestion tool."""
from typing import Any, Dict

class AskUserQuestionTool:
    name = "ask_user_question"
    description = "Ask user a question"

    async def execute(self, params: Dict[str, Any]) -> Any:
        return {"status": "ok"}

__all__ = ['AskUserQuestionTool']