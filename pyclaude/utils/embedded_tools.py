"""
Embedded search tools utilities.

Check if this build has bfs/ugrep embedded in the binary.
"""

import os
import sys

# Placeholder for is_env_truthy
def _is_env_truthy(env_var) -> bool:
    if not env_var:
        return False
    if isinstance(env_var, bool):
        return env_var
    return str(env_var).lower().strip() in ("1", "true", "yes", "on")


def has_embedded_search_tools() -> bool:
    """Check if this build has embedded search tools (bfs/ugrep).

    Returns:
        True if embedded search tools are available
    """
    if not _is_env_truthy(os.environ.get("EMBEDDED_SEARCH_TOOLS")):
        return False

    entrypoint = os.environ.get("CLAUDE_CODE_ENTRYPOINT")
    return entrypoint not in ("sdk-ts", "sdk-py", "sdk-cli", "local-agent")


def embedded_search_tools_binary_path() -> str:
    """Get path to the binary containing embedded search tools.

    Returns:
        Path to the executable
    """
    return sys.executable


__all__ = [
    "has_embedded_search_tools",
    "embedded_search_tools_binary_path",
]