"""
Context suggestions utilities.

Suggest context improvements.
"""

from typing import List, Dict, Any


def suggest_context_improvements(
    context: Dict[str, Any],
) -> List[str]:
    """Suggest improvements for context.

    Args:
        context: Current context

    Returns:
        List of suggestions
    """
    suggestions = []

    if context.get("tokens", 0) > 100000:
        suggestions.append("Consider reducing context size")

    if not context.get("system_prompt"):
        suggestions.append("Add system prompt for better guidance")

    return suggestions


__all__ = ["suggest_context_improvements"]