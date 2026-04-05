"""Cost tracking for API usage."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class CostState:
    """Tracks API usage costs."""
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_input_tokens: int = 0
    total_cache_creation_input_tokens: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    total_api_duration: float = 0.0
    total_duration: float = 0.0
    total_tool_duration: float = 0.0
    total_web_search_requests: int = 0
    session_id: str = ""
    has_unknown_model_cost: bool = False


# Global cost state
_cost_state = CostState()


def get_cost_counter() -> CostState:
    """Get current cost counter."""
    return _cost_state


def get_total_cost_usd() -> float:
    """Get total cost in USD."""
    return _cost_state.total_cost_usd


def get_total_input_tokens() -> int:
    """Get total input tokens."""
    return _cost_state.total_input_tokens


def get_total_output_tokens() -> int:
    """Get total output tokens."""
    return _cost_state.total_output_tokens


def get_total_cache_read_input_tokens() -> int:
    """Get total cache read input tokens."""
    return _cost_state.total_cache_read_input_tokens


def get_total_cache_creation_input_tokens() -> int:
    """Get total cache creation input tokens."""
    return _cost_state.total_cache_creation_input_tokens


def get_total_lines_added() -> int:
    """Get total lines added."""
    return _cost_state.total_lines_added


def get_total_lines_removed() -> int:
    """Get total lines removed."""
    return _cost_state.total_lines_removed


def get_total_api_duration() -> float:
    """Get total API duration in seconds."""
    return _cost_state.total_api_duration


def get_total_duration() -> float:
    """Get total duration in seconds."""
    return _cost_state.total_duration


def get_total_tool_duration() -> float:
    """Get total tool duration in seconds."""
    return _cost_state.total_tool_duration


def get_total_web_search_requests() -> int:
    """Get total web search requests."""
    return _cost_state.total_web_search_requests


def get_session_id() -> str:
    """Get current session ID."""
    return _cost_state.session_id


def has_unknown_model_cost() -> bool:
    """Check if any unknown model cost was encountered."""
    return _cost_state.has_unknown_model_cost


def set_has_unknown_model_cost(value: bool) -> None:
    """Set unknown model cost flag."""
    _cost_state.has_unknown_model_cost = value


def add_to_total_cost_state(cost: float, input_tokens: int, output_tokens: int) -> None:
    """Add to total cost state."""
    _cost_state.total_cost_usd += cost
    _cost_state.total_input_tokens += input_tokens
    _cost_state.total_output_tokens += output_tokens


def add_to_total_lines_changed(lines_added: int, lines_removed: int) -> None:
    """Add to total lines changed."""
    _cost_state.total_lines_added += lines_added
    _cost_state.total_lines_removed += lines_removed


def reset_cost_state() -> None:
    """Reset cost state to initial values."""
    global _cost_state
    _cost_state = CostState()


def reset_state_for_tests() -> None:
    """Reset state for tests."""
    reset_cost_state()


__all__ = [
    'CostState',
    'get_cost_counter',
    'get_total_cost_usd',
    'get_total_input_tokens',
    'get_total_output_tokens',
    'get_total_cache_read_input_tokens',
    'get_total_cache_creation_input_tokens',
    'get_total_lines_added',
    'get_total_lines_removed',
    'get_total_api_duration',
    'get_total_duration',
    'get_total_tool_duration',
    'get_total_web_search_requests',
    'get_session_id',
    'has_unknown_model_cost',
    'set_has_unknown_model_cost',
    'add_to_total_cost_state',
    'add_to_total_lines_changed',
    'reset_cost_state',
    'reset_state_for_tests',
]