"""Initialize REPL bridge."""

import asyncio
from typing import Optional, Dict, Any

from .repl_bridge import ReplBridge
from .bridge_config import get_bridge_url
from .bridge_enabled import is_bridge_enabled


async def init_repl_bridge(
    session_id: str,
    config: Optional[Dict[str, Any]] = None,
) -> Optional[ReplBridge]:
    """Initialize the REPL bridge."""
    if not is_bridge_enabled():
        return None

    config = config or {}
    url = config.get('url', get_bridge_url())

    bridge = ReplBridge(session_id=session_id, url=url)
    await bridge.connect()

    return bridge


async def cleanup_repl_bridge(bridge: Optional[ReplBridge]) -> None:
    """Clean up REPL bridge."""
    if bridge:
        await bridge.disconnect()


__all__ = ['init_repl_bridge', 'cleanup_repl_bridge']