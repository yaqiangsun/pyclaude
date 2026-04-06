"""
Internal logging service for recording events in ant environment.
"""
import os
from typing import Optional, Dict, Any
from functools import lru_cache


def is_ant_user() -> bool:
    """Check if running as an ant user."""
    return os.environ.get('USER_TYPE') == 'ant'


@lru_cache(maxsize=1)
def get_kubernetes_namespace() -> Optional[str]:
    """
    Get the current Kubernetes namespace.
    Returns None on laptops/local development,
    "default" for devboxes in default namespace,
    "ts" for devboxes in ts namespace.
    """
    if not is_ant_user():
        return None

    namespace_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
    namespace_not_found = 'namespace not found'

    try:
        with open(namespace_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return namespace_not_found
    except Exception:
        return namespace_not_found


@lru_cache(maxsize=1)
def get_container_id() -> Optional[str]:
    """
    Get the OCI container ID from within a running container.
    """
    if not is_ant_user():
        return None

    container_id_path = '/proc/self/mountinfo'
    container_id_not_found = 'container ID not found'
    container_id_not_found_in_mountinfo = 'container ID not found in mountinfo'

    try:
        with open(container_id_path, 'r') as f:
            mountinfo = f.read().strip()

        # Pattern to match both Docker and containerd/CRI-O container IDs
        # Docker: /docker/containers/[64-char-hex]
        # Containerd: /sandboxes/[64-char-hex]
        import re
        pattern = r'(?:\/docker\/containers\/|\/sandboxes\/)([0-9a-f]{64})'

        for line in mountinfo.split('\n'):
            match = re.search(pattern, line)
            if match and match.group(1):
                return match.group(1)

        return container_id_not_found_in_mountinfo
    except FileNotFoundError:
        return container_id_not_found
    except Exception:
        return container_id_not_found


async def log_permission_context_for_ants(
    tool_permission_context: Optional[Dict[str, Any]],
    moment: str = 'summary',
) -> None:
    """
    Logs an event with the current namespace and tool permission context.

    Args:
        tool_permission_context: The tool permission context to log
        moment: Either 'summary' or 'initialization'
    """
    if not is_ant_user():
        return

    import json

    # In full implementation, would call logEvent from analytics
    # For now, just return
    pass


__all__ = [
    'is_ant_user',
    'get_kubernetes_namespace',
    'get_container_id',
    'log_permission_context_for_ants',
]