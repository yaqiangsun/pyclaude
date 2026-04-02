"""
Context module - React context providers.

Note: The Python version doesn't use React context.
This directory is kept for structure compatibility.
"""
from typing import Any, List


async def get_system_prompt(
    tools: List[Any],
    main_loop_model: str,
    additional_working_directories: List[str],
    mcp_clients: List[Any],
) -> List[str]:
    """Get the system prompt parts."""
    # Simplified system prompt
    return [
        "You are Claude Code, an AI coding assistant.",
        "Use the available tools to help the user with their tasks.",
    ]


async def get_user_context() -> dict:
    """Get user context."""
    return {}


async def get_system_context() -> dict:
    """Get system context."""
    return {}


__all__ = [
    'get_system_prompt',
    'get_user_context',
    'get_system_context',
]