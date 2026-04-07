# Bash Tool UI - Python implementation for bash tool UI rendering
# Reference: src/tools/BashTool/UI.tsx (simplified)

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


# Constants for command display
MAX_COMMAND_DISPLAY_LINES = 2
MAX_COMMAND_DISPLAY_CHARS = 160


@dataclass
class BashProgress:
    """Progress information for bash tool"""
    command: str
    status: str  # "running", "completed", "error"
    output: Optional[str] = None
    exit_code: Optional[int] = None


def render_tool_use_message(command: str, description: Optional[str] = None) -> str:
    """Render the tool use message"""
    if description:
        return f"$ {command}  # {description}"
    return f"$ {command}"


def render_tool_use_error_message(error: str) -> str:
    """Render error message for tool use"""
    return f"[Bash Error] {error}"


def render_tool_use_progress_message(progress: BashProgress) -> str:
    """Render progress message for running command"""
    return f"[Running] {progress.command}"


def render_tool_use_queued_message(position: int) -> str:
    """Render queued message for command waiting in queue"""
    return f"[Queued] Command #{position}"


def truncate_command(command: str) -> str:
    """Truncate command for display"""
    lines = command.split('\n')
    if len(lines) > MAX_COMMAND_DISPLAY_LINES:
        truncated = '\n'.join(lines[:MAX_COMMAND_DISPLAY_LINES])
    else:
        truncated = command

    if len(truncated) > MAX_COMMAND_DISPLAY_CHARS:
        truncated = truncated[:MAX_COMMAND_DISPLAY_CHARS]

    return truncated.strip()


def background_hint(on_background: Optional[Any] = None) -> str:
    """Render background hint"""
    return "[Press Ctrl+B to background all running commands]"


def extract_bash_comment_label(command: str) -> Optional[str]:
    """Extract comment label from command (e.g., # description)"""
    lines = command.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            return line[1:].strip()
    return None


def parse_sed_edit_command(command: str) -> Optional[Dict[str, Any]]:
    """Parse sed edit command if applicable"""
    # This is a placeholder - the actual implementation is in sed_edit_parser.py
    from .sed_edit_parser import parse_sed_edit_command as parse_sed
    return parse_sed(command)


class BackgroundHintComponent:
    """Component for showing background hint"""

    @staticmethod
    def render(on_background: Optional[Any] = None) -> str:
        return background_hint(on_background)