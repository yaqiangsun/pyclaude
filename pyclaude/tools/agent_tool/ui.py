# Agent Tool UI - Python implementation for agent tool UI rendering
# Reference: src/tools/AgentTool/UI.tsx (simplified)

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentProgressLine:
    """Represents a progress line in agent execution"""
    text: str
    tool_name: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class AgentToolOutput:
    """Output from agent tool execution"""
    agent_type: str
    description: str
    status: str  # "success", "error", "in_progress"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress_messages: List[str] = None

    def __post_init__(self):
        if self.progress_messages is None:
            self.progress_messages = []


def render_tool_use_message(
    description: str,
    subagent_type: Optional[str] = None
) -> str:
    """Render the tool use message"""
    agent_type_str = f" ({subagent_type})" if subagent_type else ""
    return f"[Agent]{agent_type_str} {description}"


def render_tool_result_message(
    output: AgentToolOutput,
    verbose: bool = False
) -> str:
    """Render the tool result message"""
    if output.status == "error":
        return f"Error: {output.error}"

    if output.status == "in_progress":
        return f"Agent running: {output.description}"

    # Success
    result_str = ""
    if verbose and output.result:
        import json
        result_str = f"\n{json.dumps(output.result, indent=2)}"

    return f"Agent completed: {output.description}{result_str}"


def render_tool_use_error_message(error: str) -> str:
    """Render error message for tool use"""
    return f"[Agent Error] {error}"


def render_tool_use_rejected_message(reason: str) -> str:
    """Render rejected message for tool use"""
    return f"[Agent Rejected] {reason}"


def render_tool_use_progress_message(
    progress: AgentProgressLine
) -> str:
    """Render progress message"""
    return f"[Agent Progress] {progress.text}"


def render_tool_use_tag(
    agent_type: str,
    description: str
) -> str:
    """Render agent tag"""
    return f"[{agent_type}] {description}"


def user_facing_name() -> str:
    """Get user-facing name for the tool"""
    return "Agent"


def user_facing_name_background_color() -> str:
    """Get background color for user-facing name"""
    return "blue"


def render_grouped_agent_tool_use(
    messages: List[Dict[str, Any]]
) -> List[str]:
    """Render grouped agent tool uses"""
    results = []
    for msg in messages:
        if msg.get("type") == "tool_use":
            results.append(render_tool_use_message(
                msg.get("description", ""),
                msg.get("subagent_type")
            ))
    return results


# Export constants
MAX_PROGRESS_MESSAGES_TO_SHOW = 3