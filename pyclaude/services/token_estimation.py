"""
Token estimation and counting service.
"""
from typing import List, Optional, Dict, Any, Protocol
import re


# Minimal values for token counting with thinking enabled
# API constraint: max_tokens must be greater than thinking.budget_tokens
TOKEN_COUNT_THINKING_BUDGET = 1024
TOKEN_COUNT_MAX_TOKENS = 2048

# Approximate tokens per character ratio
TOKENS_PER_CHARACTER = 0.25


class Message(Protocol):
    """Protocol for message type."""
    role: str
    content: Any


def has_thinking_blocks(messages: List[Message]) -> bool:
    """
    Check if messages contain thinking blocks.

    Args:
        messages: List of messages to check

    Returns:
        True if any message has thinking blocks
    """
    for message in messages:
        if hasattr(message, 'role') and message.role == 'assistant':
            content = getattr(message, 'content', None)
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get('type')
                        if block_type in ('thinking', 'redacted_thinking'):
                            return True
    return False


def estimate_tokens_from_text(text: str) -> int:
    """
    Estimate token count from text using character-based approximation.

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return int(len(text) * TOKENS_PER_CHARACTER)


def estimate_tokens_from_messages(messages: List[Message]) -> int:
    """
    Estimate total tokens from a list of messages.

    Args:
        messages: List of messages to estimate

    Returns:
        Estimated total token count
    """
    total = 0
    for message in messages:
        content = getattr(message, 'content', '')
        if isinstance(content, str):
            total += estimate_tokens_from_text(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, str):
                    total += estimate_tokens_from_text(block)
                elif isinstance(block, dict):
                    # Handle different block types
                    text_content = block.get('text', '')
                    if text_content:
                        total += estimate_tokens_from_text(text_content)
    return total


def estimate_tokens_from_tools(tools: List[Dict[str, Any]]) -> int:
    """
    Estimate token count from tool definitions.

    Args:
        tools: List of tool definitions

    Returns:
        Estimated token count
    """
    total = 0
    for tool in tools:
        # Include tool name and description
        name = tool.get('name', '')
        description = tool.get('description', '')
        total += estimate_tokens_from_text(name)
        total += estimate_tokens_from_text(description)

        # Include input schema
        input_schema = tool.get('input_schema', {})
        if input_schema:
            import json
            total += estimate_tokens_from_text(json.dumps(input_schema))

    return total


async def count_tokens(
    text: str,
    model: str = "claude-sonnet-4-20250514",
) -> int:
    """
    Count tokens using the API.

    Args:
        text: Text to count tokens for
        model: Model to use for counting

    Returns:
        Token count
    """
    # In full implementation, would call the Claude API
    # For now, use estimation
    return estimate_tokens_from_text(text)


async def count_messages_tokens(
    messages: List[Message],
    model: str = "claude-sonnet-4-20250514",
) -> int:
    """
    Count tokens in messages using the API.

    Args:
        messages: Messages to count tokens for
        model: Model to use for counting

    Returns:
        Token count
    """
    # In full implementation, would call the Claude API
    return estimate_tokens_from_messages(messages)


__all__ = [
    'TOKEN_COUNT_THINKING_BUDGET',
    'TOKEN_COUNT_MAX_TOKENS',
    'has_thinking_blocks',
    'estimate_tokens_from_text',
    'estimate_tokens_from_messages',
    'estimate_tokens_from_tools',
    'count_tokens',
    'count_messages_tokens',
]