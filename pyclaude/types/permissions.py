"""Types for permissions."""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class PermissionLevel(str, Enum):
    """Permission levels."""
    DENY = 'deny'
    PROMPT = 'prompt'
    ALLOW = 'allow'


@dataclass
class Permission:
    """A permission."""
    name: str
    level: PermissionLevel = PermissionLevel.PROMPT
    description: str = ''


@dataclass
class PermissionResult:
    """Result of a permission check."""
    allowed: bool
    reason: Optional[str] = None


@dataclass
class PermissionContext:
    """Context for permission request."""
    tool_name: str
    resource: str
    details: Dict[str, Any] = field(default_factory=dict)


# Default permissions
DEFAULT_PERMISSIONS: Dict[str, PermissionLevel] = {
    'bash': PermissionLevel.PROMPT,
    'read': PermissionLevel.ALLOW,
    'write': PermissionLevel.PROMPT,
    'edit': PermissionLevel.PROMPT,
    'glob': PermissionLevel.ALLOW,
    'grep': PermissionLevel.ALLOW,
    'web_fetch': PermissionLevel.PROMPT,
    'web_search': PermissionLevel.PROMPT,
}


def get_default_permission(tool_name: str) -> PermissionLevel:
    """Get default permission for a tool."""
    return DEFAULT_PERMISSIONS.get(tool_name, PermissionLevel.PROMPT)


__all__ = [
    'PermissionLevel',
    'Permission',
    'PermissionResult',
    'PermissionContext',
    'DEFAULT_PERMISSIONS',
    'get_default_permission',
]