"""Bridge status utilities."""

from typing import Dict, Any, Optional
from enum import Enum

from .types import BridgeState


class BridgeStatusLevel(str, Enum):
    """Status level for bridge."""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SUCCESS = 'success'


def get_bridge_status_info(state: BridgeState) -> Dict[str, Any]:
    """Get status information for bridge state."""
    status_map = {
        BridgeState.DISABLED: {
            'level': BridgeStatusLevel.INFO,
            'message': 'Bridge is disabled',
            'can_connect': True,
        },
        BridgeState.ENABLED: {
            'level': BridgeStatusLevel.INFO,
            'message': 'Bridge is enabled',
            'can_connect': True,
        },
        BridgeState.CONNECTING: {
            'level': BridgeStatusLevel.WARNING,
            'message': 'Connecting to bridge...',
            'can_connect': False,
        },
        BridgeState.CONNECTED: {
            'level': BridgeStatusLevel.SUCCESS,
            'message': 'Connected to bridge',
            'can_disconnect': True,
        },
        BridgeState.RECONNECTING: {
            'level': BridgeStatusLevel.WARNING,
            'message': 'Reconnecting to bridge...',
            'can_connect': False,
        },
        BridgeState.ERROR: {
            'level': BridgeStatusLevel.ERROR,
            'message': 'Bridge error',
            'can_retry': True,
        },
    }
    return status_map.get(state, {})


def format_bridge_status(state: BridgeState) -> str:
    """Format bridge status as string."""
    info = get_bridge_status_info(state)
    return info.get('message', 'Unknown state')


__all__ = ['BridgeStatusLevel', 'get_bridge_status_info', 'format_bridge_status']