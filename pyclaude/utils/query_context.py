"""
Query context utilities.

Context for query operations.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class QueryContext:
    """Context for query operations."""
    query: str
    model: str
    max_tokens: Optional[int] = None
    temperature: float = 1.0
    system_prompt: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)


def create_query_context(
    query: str,
    model: str,
    **kwargs,
) -> QueryContext:
    """Create query context.

    Args:
        query: User query
        model: Model to use
        **kwargs: Additional context options

    Returns:
        Query context
    """
    return QueryContext(
        query=query,
        model=model,
        **kwargs,
    )


def add_to_history(
    context: QueryContext,
    role: str,
    content: str,
) -> None:
    """Add message to query history.

    Args:
        context: Query context
        role: Message role
        content: Message content
    """
    context.history.append({
        "role": role,
        "content": content,
    })


async def fetch_system_prompt_parts(
    tools: list,
    main_loop_model: str,
    additional_working_directories: list = None,
    mcp_clients: list = None,
    custom_system_prompt: str = None,
    append_system_prompt: str = None,
) -> dict:
    """Fetch system prompt parts for the API."""
    # Build default system prompt
    default_prompt = _build_default_system_prompt(tools, main_loop_model)

    # Add custom prompts
    if custom_system_prompt:
        default_prompt = custom_system_prompt + "\n\n" + default_prompt

    if append_system_prompt:
        default_prompt = default_prompt + "\n\n" + append_system_prompt

    return {
        'default_system_prompt': default_prompt,
        'user_context': '',
        'system_context': {},
    }


def _build_default_system_prompt(tools: list, model: str) -> str:
    """Build the default system prompt."""
    tool_descriptions = []
    for tool in tools:
        if hasattr(tool, 'name') and hasattr(tool, 'description'):
            tool_descriptions.append(f"- {tool.name}: {tool.description}")

    tools_section = ""
    if tool_descriptions:
        tools_section = "\n\n## Available Tools\n" + "\n".join(tool_descriptions)

    return f"""You are Claude Code, an AI programming assistant.

You help users write, edit, and understand code. When the user asks you to make changes, you should:
- Make minimal changes that address the user's request
- Prefer concrete code changes over long explanations
- Consider security implications
- Think about edge cases{tools_section}

You have access to various tools to interact with the filesystem and run commands.
"""


__all__ = [
    "QueryContext",
    "create_query_context",
    "add_to_history",
    "fetch_system_prompt_parts",
]