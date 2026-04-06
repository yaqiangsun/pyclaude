"""Bridge permission callbacks."""

from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
from enum import Enum


class PermissionType(str, Enum):
    """Types of permissions."""
    TOOL_USE = 'tool_use'
    FILE_ACCESS = 'file_access'
    NETWORK = 'network'
    EXECUTE = 'execute'


class PermissionResult(str, Enum):
    """Permission result."""
    ALLOW = 'allow'
    DENY = 'deny'
    ASK = 'ask'


@dataclass
class PermissionRequest:
    """A permission request."""
    type: PermissionType
    resource: str
    details: Dict[str, Any] = field(default_factory=dict)


# Permission callbacks
_permission_callbacks: Dict[str, Callable] = {}


def set_permission_callback(
    permission_type: str,
    callback: Callable[[PermissionRequest], PermissionResult],
) -> None:
    """Set a permission callback."""
    _permission_callbacks[permission_type] = callback


def get_permission_callback(permission_type: str) -> Optional[Callable]:
    """Get a permission callback."""
    return _permission_callbacks.get(permission_type)


async def request_permission(request: PermissionRequest) -> PermissionResult:
    """Request permission."""
    callback = get_permission_callback(request.type.value)
    if callback:
        return await callback(request)
    return PermissionResult.ALLOW


__all__ = [
    'PermissionType',
    'PermissionResult',
    'PermissionRequest',
    'set_permission_callback',
    'get_permission_callback',
    'request_permission',
]