"""Tool limits constants."""

from typing import Dict


# Tool use limits
MAX_TOOL_USE_PER_TURN = 100
MAX_CONCURRENT_TOOL_USES = 10
TOOL_USE_TIMEOUT_SECONDS = 300

# Rate limits
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_TOKENS_PER_MINUTE = 100000

# Token limits per model
MODEL_TOKEN_LIMITS: Dict[str, Dict[str, int]] = {
    'claude-opus-4-5': {
        'max_tokens': 200000,
        'max_input': 180000,
        'max_output': 4096,
    },
    'claude-sonnet-4-5': {
        'max_tokens': 200000,
        'max_input': 180000,
        'max_output': 8192,
    },
    'claude-haiku-4-5': {
        'max_tokens': 200000,
        'max_input': 180000,
        'max_output': 4096,
    },
}


def get_model_token_limit(model: str, limit_type: str = 'max_tokens') -> int:
    """Get token limit for a model."""
    model_base = model.split('-')[0] + '-' + model.split('-')[1]
    limits = MODEL_TOKEN_LIMITS.get(model_base, {})
    return limits.get(limit_type, 200000)


__all__ = [
    'MAX_TOOL_USE_PER_TURN',
    'MAX_CONCURRENT_TOOL_USES',
    'TOOL_USE_TIMEOUT_SECONDS',
    'RATE_LIMIT_REQUESTS_PER_MINUTE',
    'RATE_LIMIT_TOKENS_PER_MINUTE',
    'MODEL_TOKEN_LIMITS',
    'get_model_token_limit',
]