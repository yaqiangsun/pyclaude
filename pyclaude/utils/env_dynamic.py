"""
Env dynamic utilities.

Dynamic environment variable handling.
"""

import os
from typing import Dict, Optional, Callable, Any


# Dynamic env var resolvers
_resolvers: Dict[str, Callable[[], str]] = {}


def register_env_resolver(name: str, resolver: Callable[[], str]) -> None:
    """Register a dynamic env var resolver.

    Args:
        name: Environment variable name
        resolver: Function that returns the value
    """
    _resolvers[name] = resolver


def get_env_var(name: str, default: Optional[str] = None) -> str:
    """Get environment variable with dynamic resolution.

    Args:
        name: Variable name
        default: Default value

    Returns:
        Variable value
    """
    if name in _resolvers:
        return _resolvers[name]()

    return os.environ.get(name, default or "")


def resolve_all_env_vars() -> Dict[str, str]:
    """Resolve all dynamic environment variables.

    Returns:
        Dict of all env vars
    """
    result = dict(os.environ)
    for name, resolver in _resolvers.items():
        result[name] = resolver()
    return result


__all__ = [
    "register_env_resolver",
    "get_env_var",
    "resolve_all_env_vars",
]