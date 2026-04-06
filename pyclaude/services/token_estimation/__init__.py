"""Token estimation service."""

from typing import Dict, Any


# Rough token estimation: 1 token ≈ 4 characters for English
# This varies by language and content type
CHARACTERS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate token count for text."""
    if not text:
        return 0
    # Simple estimation: count characters and divide by chars per token
    # This is a rough approximation
    return len(text) // CHARACTERS_PER_TOKEN


def estimate_tokens_from_messages(messages: list) -> int:
    """Estimate tokens from message list."""
    total = 0
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, str):
                total += estimate_tokens(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text = block.get('text', '')
                        total += estimate_tokens(text)
    return total


def estimate_api_tokens(prompt: str, completion: str) -> Dict[str, int]:
    """Estimate API tokens for prompt + completion."""
    return {
        'prompt_tokens': estimate_tokens(prompt),
        'completion_tokens': estimate_tokens(completion),
        'total_tokens': estimate_tokens(prompt) + estimate_tokens(completion),
    }


__all__ = ['estimate_tokens', 'estimate_tokens_from_messages', 'estimate_api_tokens']