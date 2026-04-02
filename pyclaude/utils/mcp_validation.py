"""
MCP validation utilities.

MCP configuration validation.
"""

from typing import Dict, Any, List, Optional


def validate_mcp_config(config: Dict[str, Any]) -> List[str]:
    """Validate MCP server configuration.

    Args:
        config: MCP config

    Returns:
        List of validation errors
    """
    errors = []

    if "mcpServers" in config:
        servers = config["mcpServers"]
        if not isinstance(servers, dict):
            errors.append("mcpServers must be an object")
        else:
            for name, server in servers.items():
                if "command" not in server:
                    errors.append(f"Server '{name}' missing 'command'")

    return errors


def normalize_mcp_server_name(name: str) -> str:
    """Normalize MCP server name.

    Args:
        name: Server name

    Returns:
        Normalized name
    """
    return name.lower().replace("_", "-").replace(" ", "-")


__all__ = [
    "validate_mcp_config",
    "normalize_mcp_server_name",
]