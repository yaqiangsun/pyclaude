"""State selectors."""

from typing import Any, Optional, Callable
from dataclasses import dataclass


# Selector type
Selector = Callable[[dict], Any]


# Basic selectors
def select_session_id(state: dict) -> str:
    """Select session ID from state."""
    return state.get('sessionId', '')


def select_model(state: dict) -> str:
    """Select model from state."""
    return state.get('model', 'claude-sonnet-4-5')


def select_messages(state: dict) -> list:
    """Select messages from state."""
    return state.get('messages', [])


def select_tools(state: dict) -> list:
    """Select tools from state."""
    return state.get('tools', [])


def select_is_loading(state: dict) -> bool:
    """Select loading state."""
    return state.get('isLoading', False)


def select_error(state: dict) -> Optional[str]:
    """Select error from state."""
    return state.get('error')


# Compound selectors
def select_message_count(state: dict) -> int:
    """Select message count."""
    return len(select_messages(state))


def select_last_message(state: dict) -> Optional[dict]:
    """Select last message."""
    messages = select_messages(state)
    return messages[-1] if messages else None


def select_has_error(state: dict) -> bool:
    """Check if state has error."""
    return select_error(state) is not None


# Memoized selector helper
@dataclass
class MemoizedSelector:
    """A memoized selector."""
    selector: Selector
    last_state: Optional[dict] = None
    last_value: Any = None

    def __call__(self, state: dict) -> Any:
        if state is self.last_state:
            return self.last_value
        self.last_state = state
        self.last_value = self.selector(state)
        return self.last_value


def memoize(selector: Selector) -> MemoizedSelector:
    """Create a memoized selector."""
    return MemoizedSelector(selector)


__all__ = [
    'Selector',
    'select_session_id',
    'select_model',
    'select_messages',
    'select_tools',
    'select_is_loading',
    'select_error',
    'select_message_count',
    'select_last_message',
    'select_has_error',
    'MemoizedSelector',
    'memoize',
]