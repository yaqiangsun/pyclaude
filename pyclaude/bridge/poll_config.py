"""Bridge poll configuration."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PollConfig:
    """Configuration for bridge polling."""
    poll_interval: float = 1.0
    max_poll_interval: float = 30.0
    backoff_factor: float = 1.5
    timeout: float = 30.0
    max_retries: int = 5


# Default poll config
DEFAULT_POLL_CONFIG = PollConfig()


def get_poll_config() -> PollConfig:
    """Get the current poll configuration."""
    return DEFAULT_POLL_CONFIG


def update_poll_config(config: Dict[str, Any]) -> None:
    """Update poll configuration."""
    global DEFAULT_POLL_CONFIG
    if 'poll_interval' in config:
        DEFAULT_POLL_CONFIG.poll_interval = config['poll_interval']
    if 'max_poll_interval' in config:
        DEFAULT_POLL_CONFIG.max_poll_interval = config['max_poll_interval']
    if 'backoff_factor' in config:
        DEFAULT_POLL_CONFIG.backoff_factor = config['backoff_factor']
    if 'timeout' in config:
        DEFAULT_POLL_CONFIG.timeout = config['timeout']
    if 'max_retries' in config:
        DEFAULT_POLL_CONFIG.max_retries = config['max_retries']


__all__ = ['PollConfig', 'DEFAULT_POLL_CONFIG', 'get_poll_config', 'update_poll_config']