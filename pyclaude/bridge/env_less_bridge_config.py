"""Environment-less bridge configuration."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class EnvLessBridgeConfig:
    """Configuration for environment-less bridge."""
    enabled: bool = False
    api_url: str = 'https://api.anthropic.com'
    ws_url: str = 'wss://ws.anthropic.com'
    auth_token: Optional[str] = None


def get_env_less_bridge_config() -> EnvLessBridgeConfig:
    """Get environment-less bridge configuration."""
    # Placeholder - would load from config/flags
    return EnvLessBridgeConfig()


def is_env_less_bridge_enabled() -> bool:
    """Check if environment-less bridge is enabled."""
    return get_env_less_bridge_config().enabled


__all__ = ['EnvLessBridgeConfig', 'get_env_less_bridge_config', 'is_env_less_bridge_enabled']