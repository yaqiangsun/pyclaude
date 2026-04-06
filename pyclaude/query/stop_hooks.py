"""
Stop hooks for query engine.
"""
from typing import List, Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class StopHook:
    """A hook that can stop the query."""
    name: str
    callback: Callable[[], bool]
    priority: int = 0


# Global stop hooks
_stop_hooks: List[StopHook] = []


def register_stop_hook(name: str, callback: Callable[[], bool], priority: int = 0) -> None:
    """Register a stop hook."""
    hook = StopHook(name=name, callback=callback, priority=priority)
    _stop_hooks.append(hook)
    _stop_hooks.sort(key=lambda h: h.priority, reverse=True)


def unregister_stop_hook(name: str) -> None:
    """Unregister a stop hook."""
    global _stop_hooks
    _stop_hooks = [h for h in _stop_hooks if h.name != name]


def should_stop() -> bool:
    """Check if any stop hook returns True."""
    for hook in _stop_hooks:
        try:
            if hook.callback():
                return True
        except Exception:
            pass
    return False


def clear_stop_hooks() -> None:
    """Clear all stop hooks."""
    global _stop_hooks
    _stop_hooks = []


def get_stop_hooks() -> List[StopHook]:
    """Get all registered stop hooks."""
    return _stop_hooks.copy()


__all__ = ['StopHook', 'register_stop_hook', 'unregister_stop_hook', 'should_stop', 'clear_stop_hooks', 'get_stop_hooks']