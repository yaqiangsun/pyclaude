"""REPL bridge transport."""

import asyncio
from typing import Optional, Any, Dict, Callable
from dataclasses import dataclass

from .types import BridgeState


@dataclass
class ReplBridgeTransport:
    """Transport layer for REPL bridge."""
    url: str
    state: BridgeState = BridgeState.DISCONNECTED
    _ws: Optional[Any] = None
    _message_callback: Optional[Callable] = None

    async def connect(self) -> bool:
        """Connect to the transport."""
        self.state = BridgeState.CONNECTING
        # Placeholder - actual WebSocket connection would go here
        await asyncio.sleep(0.1)
        self.state = BridgeState.CONNECTED
        return True

    async def disconnect(self) -> None:
        """Disconnect from the transport."""
        self.state = BridgeState.DISCONNECTED
        self._ws = None

    async def send(self, data: Dict[str, Any]) -> bool:
        """Send data through transport."""
        if self.state != BridgeState.CONNECTED:
            return False
        # Placeholder - actual send would go here
        return True

    async def receive(self) -> Optional[Dict[str, Any]]:
        """Receive data from transport."""
        if self.state != BridgeState.CONNECTED:
            return None
        # Placeholder - actual receive would go here
        return None

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.state == BridgeState.CONNECTED


__all__ = ['ReplBridgeTransport']