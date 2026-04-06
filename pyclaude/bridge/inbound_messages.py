"""Inbound messages handling."""

from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass

from .types import BridgeMessage


@dataclass
class InboundMessage:
    """Inbound message from bridge."""
    raw: Dict[str, Any]
    message_type: str
    session_id: Optional[str] = None
    payload: Dict[str, Any] = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = self.raw.get('payload', {})


class InboundMessageHandler:
    """Handler for inbound messages."""

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a message type."""
        self._handlers[message_type] = handler

    async def handle_message(self, message: BridgeMessage) -> Optional[Any]:
        """Handle an inbound message."""
        handler = self._handlers.get(message.type)
        if handler:
            return await handler(message)
        return None

    def get_handler(self, message_type: str) -> Optional[Callable]:
        """Get handler for message type."""
        return self._handlers.get(message_type)


# Global handler instance
_inbound_handler = InboundMessageHandler()


def get_inbound_handler() -> InboundMessageHandler:
    """Get the global inbound message handler."""
    return _inbound_handler


__all__ = ['InboundMessage', 'InboundMessageHandler', 'get_inbound_handler']