"""
Dependencies for query engine.
"""
from typing import List, Dict, Any, Optional


class QueryDeps:
    """Dependencies for the query engine."""

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.tools: List[Dict[str, Any]] = []
        self.model: str = "claude-sonnet-4-20250514"
        self.system_prompt: str = ""
        self.max_tokens: int = 8192

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append({"role": role, "content": content})

    def add_tool(self, tool: Dict[str, Any]) -> None:
        """Add a tool to the available tools."""
        self.tools.append(tool)


def create_query_deps(
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 8192,
) -> QueryDeps:
    """Create a new QueryDeps instance."""
    deps = QueryDeps()
    deps.model = model
    deps.max_tokens = max_tokens
    return deps


__all__ = ['QueryDeps', 'create_query_deps']