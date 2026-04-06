"""Bridge enabled state management."""

from typing import Optional


_bridge_enabled: bool = False
_bridge_disabled_reason: Optional[str] = None


def is_bridge_enabled() -> bool:
    """Check if bridge is enabled."""
    return _bridge_enabled


def set_bridge_enabled(enabled: bool) -> None:
    """Set bridge enabled state."""
    global _bridge_enabled
    _bridge_enabled = enabled


def get_bridge_disabled_reason() -> Optional[str]:
    """Get reason why bridge is disabled."""
    return _bridge_disabled_reason


def set_bridge_disabled_reason(reason: Optional[str]) -> None:
    """Set bridge disabled reason."""
    global _bridge_disabled_reason
    _bridge_disabled_reason = reason


def is_env_less_bridge_enabled() -> bool:
    """Check if environment-less bridge is enabled."""
    # Placeholder - actual implementation would check feature flags
    return False


async def check_bridge_min_version() -> Optional[str]:
    """Check if bridge version meets minimum requirements."""
    # Placeholder - actual implementation would check version
    return None


async def check_env_less_bridge_min_version() -> Optional[str]:
    """Check if env-less bridge version meets minimum requirements."""
    # Placeholder - actual implementation would check version
    return None


__all__ = [
    'is_bridge_enabled',
    'set_bridge_enabled',
    'get_bridge_disabled_reason',
    'set_bridge_disabled_reason',
    'is_env_less_bridge_enabled',
    'check_bridge_min_version',
    'check_env_less_bridge_min_version',
]