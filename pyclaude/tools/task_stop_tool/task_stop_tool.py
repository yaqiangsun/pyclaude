# Task Stop Tool - Stop a running background task by ID
# Reference: src/tools/TaskStopTool/TaskStopTool.ts

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from .prompt import TASK_STOP_TOOL_NAME, DESCRIPTION


class InputSchema(BaseModel):
    """Input schema for TaskStopTool"""
    task_id: Optional[str] = Field(
        default=None,
        description="The ID of the background task to stop"
    )
    shell_id: Optional[str] = Field(
        default=None,
        description="Deprecated: use task_id instead"
    )


class OutputSchema(BaseModel):
    """Output schema for TaskStopTool"""
    message: str = Field(description="Status message about the operation")
    task_id: str = Field(description="The ID of the task that was stopped")
    task_type: str = Field(description="The type of the task that was stopped")
    command: Optional[str] = Field(
        default=None,
        description="The command or description of the stopped task"
    )


class TaskStopTool:
    """Tool for stopping a running background task by its ID"""

    name: str = TASK_STOP_TOOL_NAME
    aliases: list[str] = ["KillShell"]  # Deprecated name for backward compatibility
    max_result_size_chars: int = 100_000
    should_defer: bool = True

    def __init__(self):
        pass

    @property
    def input_schema(self) -> type[BaseModel]:
        return InputSchema

    @property
    def output_schema(self) -> type[BaseModel]:
        return OutputSchema

    def to_auto_classifier_input(self, input_data: Dict[str, Any]) -> str:
        """Convert input to auto classifier format"""
        return input_data.get("task_id") or input_data.get("shell_id") or ""

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        get_app_state: Any
    ) -> Dict[str, Any]:
        """Validate the input parameters"""
        task_id = input_data.get("task_id") or input_data.get("shell_id")

        if not task_id:
            return {
                "result": False,
                "message": "Missing required parameter: task_id",
                "error_code": 1
            }

        app_state = get_app_state()
        task = app_state.tasks.get(task_id) if app_state.tasks else None

        if not task:
            return {
                "result": False,
                "message": f"No task found with ID: {task_id}",
                "error_code": 1
            }

        if task.status != "running":
            return {
                "result": False,
                "message": f"Task {task_id} is not running (status: {task.status})",
                "error_code": 3
            }

        return {"result": True}

    async def description(self) -> str:
        """Get the tool description"""
        return "Stop a running background task by ID"

    async def prompt(self) -> str:
        """Get the tool prompt"""
        return DESCRIPTION

    def map_tool_result_to_tool_result_block_param(
        self,
        output: OutputSchema,
        tool_use_id: str
    ) -> Dict[str, Any]:
        """Map tool result to tool result block parameter"""
        import json
        return {
            "tool_use_id": tool_use_id,
            "type": "tool_result",
            "content": json.dumps(output.model_dump())
        }

    def render_tool_use_message(self) -> str:
        """Render the tool use message"""
        return ""

    def render_tool_result_message(
        self,
        output: OutputSchema,
        progress_messages: list[Any],
        verbose: bool = False
    ) -> str:
        """Render the tool result message"""
        raw_command = output.command or ""
        command = raw_command if verbose else self._truncate_command(raw_command)
        suffix = "… · stopped" if command != raw_command else " · stopped"
        return f"{command}{suffix}"

    def _truncate_command(self, command: str) -> str:
        """Truncate command for display"""
        max_lines = 2
        max_chars = 160

        lines = command.split("\n")
        if len(lines) > max_lines:
            truncated = "\n".join(lines[:max_lines])
        else:
            truncated = command

        # Simple width check (assuming 1 char = 1 width for simplicity)
        if len(truncated) > max_chars:
            truncated = truncated[:max_chars]

        return truncated.strip()

    async def call(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the tool"""
        task_id = input_data.get("task_id") or input_data.get("shell_id")

        if not task_id:
            raise ValueError("Missing required parameter: task_id")

        get_app_state = context.get("get_app_state")
        set_app_state = context.get("set_app_state")

        # Import here to avoid circular imports
        from pyclaude.pyclaude.tasks import stop_task

        result = await stop_task(task_id, {
            "get_app_state": get_app_state,
            "set_app_state": set_app_state,
        })

        return {
            "data": {
                "message": f"Successfully stopped task: {result['task_id']} ({result['command']})",
                "task_id": result["task_id"],
                "task_type": result["task_type"],
                "command": result.get("command"),
            }
        }


# Export the tool instance
task_stop_tool = TaskStopTool()