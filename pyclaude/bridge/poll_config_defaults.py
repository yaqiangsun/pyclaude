"""Poll config defaults."""

from .poll_config import PollConfig, DEFAULT_POLL_CONFIG


# Default values for poll configuration
POLL_CONFIG_DEFAULTS = {
    'poll_interval': 1.0,
    'max_poll_interval': 30.0,
    'backoff_factor': 1.5,
    'timeout': 30.0,
    'max_retries': 5,
}


def get_poll_config_defaults() -> dict:
    """Get poll config default values."""
    return POLL_CONFIG_DEFAULTS.copy()


def reset_poll_config() -> None:
    """Reset poll config to defaults."""
    global DEFAULT_POLL_CONFIG
    DEFAULT_POLL_CONFIG = PollConfig()


__all__ = ['POLL_CONFIG_DEFAULTS', 'get_poll_config_defaults', 'reset_poll_config']