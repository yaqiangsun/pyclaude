"""Context management for Claude Code."""
import os
from functools import lru_cache
from typing import Optional, Dict, Any


# Maximum status characters
MAX_STATUS_CHARS = 2000

# System prompt injection for cache breaking
_system_prompt_injection: Optional[str] = None


def get_system_prompt_injection() -> Optional[str]:
    """Get system prompt injection."""
    return _system_prompt_injection


def set_system_prompt_injection(value: Optional[str]) -> None:
    """Set system prompt injection and clear caches."""
    global _system_prompt_injection
    _system_prompt_injection = value
    # Clear context caches
    get_user_context.cache_clear()
    get_system_context.cache_clear()


@lru_cache(maxsize=1)
def get_git_status() -> Optional[str]:
    """Get git status for current directory."""
    # Implementation would run git status
    return None


@lru_cache(maxsize=1)
def get_user_context() -> Dict[str, Any]:
    """Get user context information."""
    return {
        'cwd': os.getcwd(),
        'git_status': get_git_status(),
    }


@lru_cache(maxsize=1)
def get_system_context() -> Dict[str, Any]:
    """Get system context information."""
    return {
        'platform': os.name,
    }


__all__ = [
    'get_system_prompt_injection',
    'set_system_prompt_injection',
    'get_git_status',
    'get_user_context',
    'get_system_context',
    'MAX_STATUS_CHARS',
]