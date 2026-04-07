"""
MCP Skill Builders - Registry for MCP skill discovery functions.

This module provides a write-once registry for the functions that
MCP skill discovery needs, avoiding circular dependencies.
"""
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SkillCommand:
    """A skill command definition."""
    name: str
    description: str
    code: str
    args: Dict[str, Any]
    source: str = "unknown"


@dataclass
class SkillFrontmatter:
    """Frontmatter parsed from a skill file."""
    name: str
    description: str
    command: Optional[str] = None
    args: Dict[str, Any] = None


# Type definitions for builders
MCPSkillBuilders = Dict[str, Any]

# Global registry
_builders: Optional[MCPSkillBuilders] = None


def register_mcp_skill_builders(builders: MCPSkillBuilders) -> None:
    """
    Register MCP skill builder functions.

    This should be called at loadSkillsDir module initialization,
    before any MCP server connects.
    """
    global _builders
    if _builders is not None:
        raise ValueError("MCP skill builders already registered")
    _builders = builders


def get_mcp_skill_builders() -> MCPSkillBuilders:
    """
    Get the registered MCP skill builders.

    Raises:
        ValueError: If builders not registered
    """
    global _builders
    if _builders is None:
        raise ValueError(
            "MCP skill builders not registered — loadSkillsDir has not been evaluated yet"
        )
    return _builders


def is_mcp_skill_builders_registered() -> bool:
    """Check if MCP skill builders are registered."""
    return _builders is not None


# Create skill command function type
CreateSkillCommandFunc = Callable[[str, str, str, Dict[str, Any], str], SkillCommand]

# Parse skill frontmatter function type
ParseSkillFrontmatterFunc = Callable[[str], SkillFrontmatter]


__all__ = [
    'SkillCommand',
    'SkillFrontmatter',
    'MCPSkillBuilders',
    'register_mcp_skill_builders',
    'get_mcp_skill_builders',
    'is_mcp_skill_builders_registered',
]