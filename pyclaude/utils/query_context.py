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


__all__ = [
    "QueryContext",
    "create_query_context",
    "add_to_history",
]