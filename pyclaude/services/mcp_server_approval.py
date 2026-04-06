"""
MCP Server Approval service - handles approval for MCP server connections.
"""
from typing import Dict, Any, Set, Optional
from dataclasses import dataclass
from enum import Enum


class ApprovalStatus(Enum):
    """Approval status for MCP server."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class MCPServerApproval:
    """Approval record for an MCP server."""
    server_name: str
    status: ApprovalStatus
    approved_at: Optional[int] = None
    denied_at: Optional[int] = None
    expires_at: Optional[int] = None
    permissions: Dict[str, bool] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = {}


# Store approved servers
_approved_servers: Dict[str, MCPServerApproval] = {}


def get_approval_status(server_name: str) -> ApprovalStatus:
    """Get the approval status for a server."""
    approval = _approved_servers.get(server_name)
    if not approval:
        return ApprovalStatus.PENDING
    return approval.status


def approve_server(
    server_name: str,
    permissions: Optional[Dict[str, bool]] = None,
    expires_at: Optional[int] = None,
) -> MCPServerApproval:
    """Approve an MCP server."""
    import time
    approval = MCPServerApproval(
        server_name=server_name,
        status=ApprovalStatus.APPROVED,
        approved_at=int(time.time()),
        expires_at=expires_at,
        permissions=permissions or {},
    )
    _approved_servers[server_name] = approval
    return approval


def deny_server(server_name: str) -> MCPServerApproval:
    """Deny an MCP server."""
    import time
    approval = MCPServerApproval(
        server_name=server_name,
        status=ApprovalStatus.DENIED,
        denied_at=int(time.time()),
    )
    _approved_servers[server_name] = approval
    return approval


def is_server_approved(server_name: str) -> bool:
    """Check if a server is approved."""
    return get_approval_status(server_name) == ApprovalStatus.APPROVED


def get_server_permissions(server_name: str) -> Dict[str, bool]:
    """Get permissions for an approved server."""
    approval = _approved_servers.get(server_name)
    if approval and approval.status == ApprovalStatus.APPROVED:
        return approval.permissions or {}
    return {}


def clear_approval(server_name: str) -> None:
    """Clear approval for a server."""
    if server_name in _approved_servers:
        del _approved_servers[server_name]


def get_all_approved_servers() -> Dict[str, MCPServerApproval]:
    """Get all approved servers."""
    return _approved_servers.copy()


__all__ = [
    'ApprovalStatus',
    'MCPServerApproval',
    'get_approval_status',
    'approve_server',
    'deny_server',
    'is_server_approved',
    'get_server_permissions',
    'clear_approval',
    'get_all_approved_servers',
]