"""
Token budget management for query engine.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TokenBudget:
    """Token budget configuration."""
    max_input_tokens: int = 200000
    max_output_tokens: int = 8192
    thinking_budget: int = 0
    reserved_for_response: int = 4096


# Default budget
DEFAULT_BUDGET = TokenBudget()


def calculate_available_for_input(budget: TokenBudget, estimated_output: int = 0) -> int:
    """
    Calculate available tokens for input given budget and expected output.

    Args:
        budget: The token budget
        estimated_output: Estimated tokens for output

    Returns:
        Available tokens for input
    """
    reserved = max(estimated_output, budget.reserved_for_response)
    return budget.max_input_tokens - budget.thinking_budget - reserved


def estimate_message_tokens(message: Dict[str, Any]) -> int:
    """
    Estimate tokens in a message.

    Args:
        message: Message to estimate

    Returns:
        Estimated token count
    """
    content = message.get('content', '')
    if isinstance(content, str):
        # Rough estimate: 1 token ≈ 4 characters
        return len(content) // 4
    elif isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, dict):
                text = block.get('text', '')
                if text:
                    total += len(text) // 4
        return total
    return 0


def estimate_tool_tokens(tool: Dict[str, Any]) -> int:
    """
    Estimate tokens in a tool definition.

    Args:
        tool: Tool definition

    Returns:
        Estimated token count
    """
    import json
    return len(json.dumps(tool)) // 4


def fits_in_budget(
    messages: list,
    tools: list,
    budget: TokenBudget = DEFAULT_BUDGET,
) -> bool:
    """
    Check if messages and tools fit in the token budget.

    Args:
        messages: List of messages
        tools: List of tool definitions
        budget: Token budget to check against

    Returns:
        True if fits in budget
    """
    total_tokens = sum(estimate_message_tokens(m) for m in messages)
    total_tokens += sum(estimate_tool_tokens(t) for t in tools)

    return total_tokens <= budget.max_input_tokens


__all__ = ['TokenBudget', 'DEFAULT_BUDGET', 'calculate_available_for_input', 'estimate_message_tokens', 'estimate_tool_tokens', 'fits_in_budget']