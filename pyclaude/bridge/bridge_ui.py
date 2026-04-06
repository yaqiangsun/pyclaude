"""Bridge UI utilities."""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BridgeUIState:
    """UI state for bridge."""
    show_dialog: bool = False
    dialog_title: str = ''
    dialog_message: str = ''
    qr_code: Optional[str] = None


def get_default_ui_state() -> BridgeUIState:
    """Get default bridge UI state."""
    return BridgeUIState()


def format_bridge_status(state: str) -> str:
    """Format bridge status for display."""
    status_map = {
        'disabled': 'Disabled',
        'enabled': 'Enabled',
        'connecting': 'Connecting...',
        'connected': 'Connected',
        'reconnecting': 'Reconnecting...',
        'error': 'Error',
    }
    return status_map.get(state, state)


__all__ = ['BridgeUIState', 'get_default_ui_state', 'format_bridge_status']