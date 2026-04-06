"""Trusted device utilities."""

import os
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


# Trusted device storage
_trusted_devices: Dict[str, Dict[str, Any]] = {}


def get_device_id() -> str:
    """Get the current device ID."""
    # Use a combination of hostname and user to create a stable device ID
    hostname = os.environ.get('HOSTNAME', 'unknown')
    username = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    device_str = f"{hostname}-{username}"
    return hashlib.sha256(device_str.encode()).hexdigest()[:16]


def is_device_trusted(device_id: str) -> bool:
    """Check if a device is trusted."""
    device = _trusted_devices.get(device_id)
    if not device:
        return False

    # Check expiration
    expires_at = device.get('expires_at')
    if expires_at and datetime.now() > expires_at:
        del _trusted_devices[device_id]
        return False

    return True


def trust_device(device_id: str, duration_days: int = 30) -> None:
    """Trust a device."""
    expires_at = datetime.now() + timedelta(days=duration_days)
    _trusted_devices[device_id] = {
        'trusted_at': datetime.now(),
        'expires_at': expires_at,
    }


def untrust_device(device_id: str) -> bool:
    """Untrust a device."""
    if device_id in _trusted_devices:
        del _trusted_devices[device_id]
        return True
    return False


def get_trusted_devices() -> Dict[str, Dict[str, Any]]:
    """Get all trusted devices."""
    return _trusted_devices.copy()


__all__ = [
    'get_device_id',
    'is_device_trusted',
    'trust_device',
    'untrust_device',
    'get_trusted_devices',
]