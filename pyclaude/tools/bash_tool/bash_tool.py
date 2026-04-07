# Bash Tool - Main bash command execution tool
# Reference: src/tools/BashTool/BashTool.tsx (simplified)

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from .tool_name import BASH_TOOL_NAME
from .prompt import get_default_timeout_ms, get_max_timeout_ms, get_simple_prompt
from .should_use_sandbox import should_use_sandbox
from .bash_permissions import (
    bash_tool_has_permission,
    command_has_any_cd,
    match_wildcard_pattern,
    permission_rule_extract_prefix
)
from .command_semantics import interpret_command_result
from .read_only_validation import check_read_only_constraints
from .sed_edit_parser import parse_sed_edit_command


class BashInputSchema(BaseModel):
    """Input schema for BashTool"""
    command: str = Field(description="The bash command to execute")
    timeout_ms: Optional[int] = Field(
        default=None,
        description="Timeout in milliseconds for the command"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of what the command does"
    )
    workdir: Optional[str] = Field(
        default=None,
        description="Working directory to run the command in"
    )


class BashOutputSchema(BaseModel):
    """Output schema for BashTool"""
    stdout: str = Field(description="Standard output from the command")
    stderr: str = Field(description="Standard error from the command")
    exit_code: int = Field(description="Exit code of the command")
    command: str = Field(description="The command that was executed")
    truncated: bool = Field(
        default=False,
        description="Whether the output was truncated"
    )


class BashTool:
    """Tool for executing bash commands"""

    name: str = BASH_TOOL_NAME
    max_result_size_chars: int = 100_000
    should_defer: bool = True

    # Command categories for collapsible display
    SEARCH_COMMANDS: set = {'find', 'grep', 'rg', 'ag', 'ack', 'locate', 'which', 'whereis'}
    READ_COMMANDS: set = {'cat', 'head', 'tail', 'less', 'more', 'wc', 'stat', 'file', 'strings', 'jq', 'awk', 'cut', 'sort', 'uniq', 'tr'}
    LIST_COMMANDS: set = {'ls', 'tree', 'du'}
    SEMANTIC_NEUTRAL_COMMANDS: set = {'echo', 'printf', 'true', 'false', ':'}

    # Progress display
    PROGRESS_THRESHOLD_MS = 2000
    ASSISTANT_BLOCKING_BUDGET_MS = 15_000

    def __init__(self):
        pass

    @property
    def input_schema(self) -> type[BaseModel]:
        return BashInputSchema

    @property
    def output_schema(self) -> type[BaseModel]:
        return BashOutputSchema

    def get_default_timeout_ms(self) -> int:
        return get_default_timeout_ms()

    def get_max_timeout_ms(self) -> int:
        return get_max_timeout_ms()

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate the input parameters"""
        command = input_data.get("command", "")

        if not command:
            return {
                "result": False,
                "message": "Missing required parameter: command",
                "error_code": 1
            }

        # Check permissions
        permission_result = await bash_tool_has_permission(command, context)
        if not permission_result.allowed:
            return {
                "result": False,
                "message": permission_result.reason or "Permission denied",
                "error_code": 2
            }

        # Check read-only constraints
        read_only_check = check_read_only_constraints(command)
        if not read_only_check.allowed:
            return {
                "result": False,
                "message": read_only_check.reason or "Command violates read-only constraints",
                "error_code": 3
            }

        return {"result": True}

    async def description(self) -> str:
        return "Execute a bash command in the terminal"

    async def prompt(self) -> str:
        return get_simple_prompt()

    def should_use_sandbox_mode(self, command: str) -> bool:
        return should_use_sandbox(command)

    def interpret_command_result(
        self,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str
    ) -> Dict[str, Any]:
        """Interpret command result for display purposes"""
        return interpret_command_result(command, exit_code, stdout, stderr)

    def is_search_command(self, command: str) -> bool:
        """Check if command is a search command"""
        cmd = command.split()[0] if command else ""
        return cmd in self.SEARCH_COMMANDS

    def is_read_command(self, command: str) -> bool:
        """Check if command is a read command"""
        cmd = command.split()[0] if command else ""
        return cmd in self.READ_COMMANDS

    def is_list_command(self, command: str) -> bool:
        """Check if command is a list command"""
        cmd = command.split()[0] if command else ""
        return cmd in self.LIST_COMMANDS

    async def call(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the bash command"""
        command = input_data.get("command", "")
        timeout_ms = input_data.get("timeout_ms") or self.get_default_timeout_ms()
        workdir = input_data.get("workdir")

        if not command:
            raise ValueError("Missing required parameter: command")

        # Import here to avoid circular imports
        from pyclaude.pyclaude.tasks import spawn_shell_task

        result = await spawn_shell_task(
            command=command,
            timeout_ms=timeout_ms,
            workdir=workdir,
            context=context
        )

        return {
            "data": {
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "exit_code": result.get("exit_code", 0),
                "command": command,
                "truncated": result.get("truncated", False),
            }
        }


# Export the tool instance
bash_tool = BashTool()