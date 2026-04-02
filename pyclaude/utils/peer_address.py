"""
Peer address parsing.

Kept separate from peer_registry.py so that SendMessageTool can import
parse_address without transitively loading the bridge modules.
"""

from typing import Dict, Optional, Tuple
import socket


def parse_address(to: str) -> Dict[str, str]:
    """Parse a URI-style address into scheme + target."""
    if to.startswith('uds:'):
        return {'scheme': 'uds', 'target': to[4:]}
    if to.startswith('bridge:'):
        return {'scheme': 'bridge', 'target': to[7:]}
    # Legacy: old-code UDS senders emit bare socket paths
    if to.startswith('/'):
        return {'scheme': 'uds', 'target': to}
    return {'scheme': 'other', 'target': to}


def get_local_ip() -> Optional[str]:
    """Get local IP address.

    Returns:
        Local IP address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def get_peer_address(host: str, port: int) -> Optional[Tuple[str, int]]:
    """Resolve peer address.

    Args:
        host: Hostname
        port: Port

    Returns:
        (address, port) tuple
    """
    try:
        return socket.getaddrinfo(host, port, socket.AF_INET)[0][4]
    except Exception:
        return None


def format_address(addr: Tuple[str, int]) -> str:
    """Format address for display.

    Args:
        addr: (host, port) tuple

    Returns:
        Formatted string
    """
    return f"{addr[0]}:{addr[1]}"


__all__ = [
    "parse_address",
    "get_local_ip",
    "get_peer_address",
    "format_address",
]