"""
Bridge types and constants.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class BridgeState(str, Enum):
    """Bridge connection states."""
    DISABLED = 'disabled'
    ENABLED = 'enabled'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    RECONNECTING = 'reconnecting'
    DISCONNECTED = 'disconnected'
    ERROR = 'error'


class BridgeEventType(str, Enum):
    """Bridge event types."""
    SESSION_START = 'session_start'
    SESSION_END = 'session_end'
    MESSAGE = 'message'
    TOOL_USE = 'tool_use'
    TOOL_RESULT = 'tool_result'
    ERROR = 'error'
    STATUS = 'status'
    TASK_STARTED = 'task_started'
    TASK_COMPLETED = 'task_completed'
    TASK_FAILED = 'task_failed'


@dataclass
class BridgeMessage:
    """Bridge message structure."""
    id: str
    type: str
    payload: dict = field(default_factory=dict)
    timestamp: int = 0
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp == 0:
            import time
            self.timestamp = int(time.time() * 1000)


@dataclass
class BridgeEvent:
    """Bridge event."""
    type: BridgeEventType
    data: dict = field(default_factory=dict)
    timestamp: int = 0

    def __post_init__(self):
        if self.timestamp == 0:
            import time
            self.timestamp = int(time.time() * 1000)


@dataclass
class BridgeConfig:
    """Bridge configuration."""
    enabled: bool = False
    url: Optional[str] = None
    api_key: Optional[str] = None
    environment_id: Optional[str] = None
    session_id: Optional[str] = None
    outbound_only: bool = False
    reconnect: bool = True
    reconnect_delay: float = 1.0
    max_reconnect_attempts: int = 10
    ping_interval: int = 30


@dataclass
class SessionInfo:
    """Session information."""
    id: str
    name: Optional[str] = None
    created_at: int = 0
    last_active: int = 0
    status: str = 'active'
    metadata: dict = field(default_factory=dict)


# Message types for bridge protocol
class BridgeMessageType(str, Enum):
    """Types of messages in bridge protocol."""
    # Control messages
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    PING = 'ping'
    PONG = 'pong'

    # Session messages
    SESSION_CREATE = 'session_create'
    SESSION_JOIN = 'session_join'
    SESSION_LEAVE = 'session_leave'
    SESSION_LIST = 'session_list'

    # Claude Code messages
    USER_MESSAGE = 'user_message'
    ASSISTANT_MESSAGE = 'assistant_message'
    TOOL_USE = 'tool_use'
    TOOL_RESULT = 'tool_result'
    SYSTEM_MESSAGE = 'system_message'

    # Event messages
    EVENT = 'event'
    ERROR = 'error'


# Permission callbacks
@dataclass
class BridgePermissionCallbacks:
    """Callbacks for permission requests."""
    on_permission_request: Optional[callable] = None
    on_permission_grant: Optional[callable] = None
    on_permission_deny: Optional[callable] = None


# Status utilities
def get_bridge_status(state: BridgeState) -> dict[str, Any]:
    """Get bridge status information."""
    return {
        'state': state.value,
        'is_connected': state == BridgeState.CONNECTED,
        'is_connecting': state == BridgeState.CONNECTING,
        'is_reconnecting': state == BridgeState.RECONNECTING,
        'has_error': state == BridgeState.ERROR,
    }


__all__ = [
    'BridgeState',
    'BridgeEventType',
    'BridgeMessage',
    'BridgeEvent',
    'BridgeConfig',
    'SessionInfo',
    'BridgeMessageType',
    'BridgePermissionCallbacks',
    'get_bridge_status',
]