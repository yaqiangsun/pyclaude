"""
Ink events - Event handling for terminal interaction.
"""
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Event types."""
    CLICK = "click"
    FOCUS = "focus"
    BLUR = "blur"
    KEY_DOWN = "keydown"
    KEY_UP = "keyup"
    MOUSE_ENTER = "mouseenter"
    MOUSE_LEAVE = "mouseleave"
    MOUSE_MOVE = "mousemove"


@dataclass
class ClickEvent:
    """Click event."""
    x: int
    y: int
    button: int = 0  # 0 = left, 1 = middle, 2 = right


@dataclass
class FocusEvent:
    """Focus event."""
    type: str  # 'focus' or 'blur'


@dataclass
class KeyboardEvent:
    """Keyboard event."""
    key: str
    alt: bool = False
    ctrl: bool = False
    shift: bool = False
    meta: bool = False


# Event handlers type
EventHandler = Callable[[Any], None]


class EventEmitter:
    """Simple event emitter."""

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {
            event_type: [] for event_type in EventType
        }

    def on(self, event: EventType, handler: EventHandler) -> None:
        """Register an event handler."""
        self._handlers[event].append(handler)

    def off(self, event: EventType, handler: EventHandler) -> None:
        """Unregister an event handler."""
        if handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def emit(self, event: EventType, data: Any) -> None:
        """Emit an event."""
        for handler in self._handlers[event]:
            try:
                handler(data)
            except Exception:
                pass

    def clear(self, event: Optional[EventType] = None) -> None:
        """Clear handlers."""
        if event:
            self._handlers[event].clear()
        else:
            for handlers in self._handlers.values():
                handlers.clear()


# Global event emitter
_emitter: Optional[EventEmitter] = None


def get_emitter() -> EventEmitter:
    """Get the global event emitter."""
    global _emitter
    if _emitter is None:
        _emitter = EventEmitter()
    return _emitter


# Convenience functions
def on_click(handler: EventHandler) -> None:
    """Register click handler."""
    get_emitter().on(EventType.CLICK, handler)


def on_key_down(handler: EventHandler) -> None:
    """Register keydown handler."""
    get_emitter().on(EventType.KEY_DOWN, handler)


def emit_click(x: int, y: int, button: int = 0) -> None:
    """Emit a click event."""
    get_emitter().emit(EventType.CLICK, ClickEvent(x=x, y=y, button=button))


def emit_key(key: str, **modifiers: bool) -> None:
    """Emit a key event."""
    get_emitter().emit(EventType.KEY_DOWN, KeyboardEvent(key=key, **modifiers))


__all__ = [
    'EventType',
    'ClickEvent',
    'FocusEvent',
    'KeyboardEvent',
    'EventEmitter',
    'get_emitter',
    'on_click',
    'on_key_down',
    'emit_click',
    'emit_key',
]