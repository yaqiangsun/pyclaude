"""
Token utilities.

Token counting and estimation.
"""

from typing import Dict, Optional
import re


# Rough token estimation (characters to tokens ratio)
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Args:
        text: Text to count

    Returns:
        Estimated token count
    """
    # Simple estimation: ~4 characters per token
    return len(text) // CHARS_PER_TOKEN


def count_tokens(text: str) -> int:
    """Count tokens more accurately.

    Args:
        text: Text to count

    Returns:
        Token count
    """
    # Split on whitespace and punctuation
    tokens = re.findall(r'\S+', text)
    return len(tokens)


def get_token_budget(model: str) -> Dict[str, int]:
    """Get token budget for model.

    Args:
        model: Model name

    Returns:
        Dict with input/output limits
    """
    budgets = {
        "claude-3-opus": {"input": 200000, "output": 4000},
        "claude-3-sonnet": {"input": 150000, "output": 4000},
        "claude-3-haiku": {"input": 150000, "output": 4000},
        "claude-4-opus": {"input": 1000000, "output": 4000},
        "claude-4-sonnet": {"input": 200000, "output": 4000},
    }

    return budgets.get(model.lower(), {"input": 100000, "output": 4000})


def calculate_tokens_remaining(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> Dict[str, int]:
    """Calculate remaining token budget.

    Args:
        model: Model name
        input_tokens: Input token count
        output_tokens: Output token count

    Returns:
        Dict with remaining counts
    """
    budget = get_token_budget(model)
    return {
        "input": budget["input"] - input_tokens,
        "output": budget["output"] - output_tokens,
    }


__all__ = [
    "CHARS_PER_TOKEN",
    "estimate_tokens",
    "count_tokens",
    "get_token_budget",
    "calculate_tokens_remaining",
]