"""
Model utilities for Claude Code.
"""

import os
from typing import Optional

from ..settings import get_setting_model


# Default models
DEFAULT_MODEL = 'claude-sonnet-4-20250514'
SONNET_MODEL = 'claude-sonnet-4-20250514'
HAIKU_MODEL = 'claude-haiku-4-20250307'
OPUS_MODEL = 'claude-opus-4-20250501'

# Model pricing (per 1M tokens)
MODEL_PRICING = {
    'claude-opus-4-20250501': {'input': 15.0, 'output': 75.0},
    'claude-sonnet-4-20250514': {'input': 3.0, 'output': 15.0},
    'claude-haiku-4-20250307': {'input': 0.8, 'output': 4.0},
    'claude-3-5-sonnet-20240620': {'input': 3.0, 'output': 15.0},
    'claude-3-opus-20240229': {'input': 15.0, 'output': 75.0},
    'claude-3-haiku-20240307': {'input': 0.8, 'output': 4.0},
}

# Context windows
MODEL_CONTEXT_WINDOWS = {
    'claude-opus-4-20250501': 200000,
    'claude-sonnet-4-20250514': 200000,
    'claude-haiku-4-20250307': 200000,
    'claude-3-5-sonnet-20240620': 200000,
    'claude-3-opus-20240229': 200000,
    'claude-3-haiku-20240307': 200000,
}


def get_main_loop_model() -> str:
    """Get the main loop model from settings, environment, or default."""
    # Priority: settings > environment variable > default

    # First check settings
    settings_model = get_setting_model()
    if settings_model:
        return settings_model

    # Check common environment variables (matching src behavior)
    # CLAUDE_MODEL is the primary env var
    env_model = os.environ.get('CLAUDE_MODEL')
    if env_model:
        return env_model

    # Also check ANTHROPIC_DEFAULT_*_MODEL variables
    # These are used by 3rd party providers
    for key in ['ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL',
                'ANTHROPIC_DEFAULT_HAIKU_MODEL', 'ANTHROPIC_MODEL']:
        env_model = os.environ.get(key)
        if env_model:
            return env_model

    return DEFAULT_MODEL


def parse_user_specified_model(model: str) -> str:
    """Parse and validate user-specified model."""
    if not model:
        return DEFAULT_MODEL
    return model


def get_model_pricing(model: str) -> dict:
    """Get pricing for a model."""
    return MODEL_PRICING.get(model, {'input': 3.0, 'output': 15.0})


def get_model_context_window(model: str) -> int:
    """Get context window for a model."""
    return MODEL_CONTEXT_WINDOWS.get(model, 200000)


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate cost for token usage."""
    pricing = get_model_pricing(model)
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    return input_cost + output_cost


def is_model_available(model: str) -> bool:
    """Check if model is available."""
    return model in MODEL_PRICING


def get_default_model() -> str:
    """Get the default model."""
    return DEFAULT_MODEL


def get_sonnet_model() -> str:
    """Get the Sonnet model."""
    return SONNET_MODEL


def get_haiku_model() -> str:
    """Get the Haiku model."""
    return HAIKU_MODEL


def get_opus_model() -> str:
    """Get the Opus model."""
    return OPUS_MODEL


# Model setting type
class ModelSetting:
    """Model setting with provider info."""

    def __init__(
        self,
        model: str,
        provider: str = 'anthropic',
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.provider = provider
        self.base_url = base_url
        self.api_key = api_key

    def to_dict(self) -> dict:
        return {
            'model': self.model,
            'provider': self.provider,
            'base_url': self.base_url,
            'api_key': self.api_key,
        }


__all__ = [
    'DEFAULT_MODEL',
    'SONNET_MODEL',
    'HAIKU_MODEL',
    'OPUS_MODEL',
    'get_main_loop_model',
    'parse_user_specified_model',
    'get_model_pricing',
    'get_model_context_window',
    'calculate_cost',
    'is_model_available',
    'get_default_model',
    'get_sonnet_model',
    'get_haiku_model',
    'get_opus_model',
    'ModelSetting',
]