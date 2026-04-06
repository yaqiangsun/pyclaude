"""REPL bridge handle."""

import asyncio
from typing import Optional, Any, Dict, Callable
from dataclasses import dataclass, field

from .types import BridgeState, BridgeMessage


@dataclass
class ReplBridgeHandle:
    """Handle for REPL bridge connection."""
    session_id: str
    state: BridgeState = BridgeState.DISABLED
    message_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def connect(self) -> bool:
        """Connect to the bridge."""
        self.state = BridgeState.CONNECTING
        # Placeholder - actual implementation would establish WebSocket connection
        self.state = BridgeState.CONNECTED
        self._running = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from the bridge."""
        self._running = False
        self.state = BridgeState.DISCONNECTED

    async def send_message(self, message: BridgeMessage) -> bool:
        """Send a message through the bridge."""
        if self.state != BridgeState.CONNECTED:
            return False
        # Placeholder - actual implementation would send via WebSocket
        return True

    async def receive_message(self) -> Optional[BridgeMessage]:
        """Receive a message from the bridge."""
        if not self._running:
            return None
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    def is_connected(self) -> bool:
        """Check if bridge is connected."""
        return self.state == BridgeState.CONNECTED


__all__ = ['ReplBridgeHandle']