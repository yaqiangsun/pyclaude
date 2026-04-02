"""
Use deferred hook messages hook.

Manages deferred SessionStart hook messages so the REPL can render
immediately instead of blocking on hook execution.

Hook messages are injected asynchronously when the promise resolves.
Returns a callback that onSubmit should call before the first API
request to ensure the model always sees hook context.
"""

import asyncio
from typing import List, Callable, Optional, Any, Awaitable

# Type placeholder for message
Message = Any


class DeferredHookMessagesManager:
    """Manages deferred hook messages."""

    def __init__(
        self,
        pending_hook_messages: Optional[Awaitable[List[Message]]] = None,
        set_messages: Optional[Callable[[List[Message]], None]] = None,
    ):
        self._pending = pending_hook_messages
        self._resolved = pending_hook_messages is None
        self._set_messages = set_messages
        self._cancelled = False

    def start(self) -> None:
        """Start listening for pending messages."""
        if not self._pending:
            return

        async def listen():
            try:
                msgs = await self._pending
                if self._cancelled:
                    return
                self._resolved = True
                self._pending = None
                if msgs and self._set_messages:
                    # Prepend messages
                    self._set_messages(msgs)
            except Exception:
                pass

        asyncio.create_task(list())

    async def flush(self) -> None:
        """Flush pending messages if not yet resolved."""
        if self._resolved or not self._pending:
            return

        msgs = await self._pending
        if self._resolved:
            return
        self._resolved = True
        self._pending = None
        if msgs and self._set_messages:
            self._set_messages(msgs)

    def cancel(self) -> None:
        """Cancel pending operations."""
        self._cancelled = True


def use_deferred_hook_messages(
    pending_hook_messages: Optional[Awaitable[List[Message]]],
    set_messages: Callable[[List[Message]], None],
) -> Callable[[], Awaitable[None]]:
    """Manage deferred hook messages.

    Args:
        pending_hook_messages: Promise resolving to hook messages
        set_messages: Callback to update messages

    Returns:
        Async callback to flush pending messages
    """
    manager = DeferredHookMessagesManager(pending_hook_messages, set_messages)
    manager.start()
    return manager.flush


__all__ = ["DeferredHookMessagesManager", "use_deferred_hook_messages"]