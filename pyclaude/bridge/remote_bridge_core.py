"""Remote bridge core functionality."""

import asyncio
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from .types import BridgeState, BridgeMessage


@dataclass
class RemoteBridgeCore:
    """Core remote bridge functionality."""
    session_id: str
    url: str
    state: BridgeState = BridgeState.DISCONNECTED
    reconnect_attempts: int = 0
    max_reconnect_attempts: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)

    async def connect(self) -> bool:
        """Connect to remote bridge."""
        self.state = BridgeState.CONNECTING
        # Placeholder - actual WebSocket connection
        await asyncio.sleep(0.1)
        self.state = BridgeState.CONNECTED
        self.reconnect_attempts = 0
        return True

    async def disconnect(self) -> None:
        """Disconnect from remote bridge."""
        self.state = BridgeState.DISCONNECTED

    async def reconnect(self) -> bool:
        """Reconnect to remote bridge."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            return False

        self.reconnect_attempts += 1
        self.state = BridgeState.RECONNECTING
        await asyncio.sleep(0.5 * self.reconnect_attempts)
        return await self.connect()

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.state == BridgeState.CONNECTED


__all__ = ['RemoteBridgeCore']