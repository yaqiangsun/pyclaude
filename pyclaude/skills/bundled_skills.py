"""Bundled Skills - Core registry and definition matching src/skills/bundledSkills.ts"""
from __future__ import annotations
import os
from typing import Any, Callable, Optional

# Bundled skill definition
class BundledSkillDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        allowed_tools: Optional[list[str]] = None,
        argument_hint: Optional[str] = None,
        when_to_use: Optional[str] = None,
        model: Optional[str] = None,
        disable_model_invocation: bool = False,
        user_invocable: bool = True,
        hooks: Optional[list] = None,
        context: Optional[dict] = None,
        agent: Optional[dict] = None,
        is_enabled: Optional[Callable[[], bool]] = None,
        get_prompt_for_command: Optional[Callable] = None,
        files: Optional[dict[str, str]] = None,
    ):
        self.name = name
        self.description = description
        self.allowed_tools = allowed_tools or []
        self.argument_hint = argument_hint
        self.when_to_use = when_to_use
        self.model = model
        self.disable_model_invocation = disable_model_invocation
        self.user_invocable = user_invocable
        self.hooks = hooks or []
        self.context = context or {}
        self.agent = agent
        self.is_enabled = is_enabled or (lambda: True)
        self.get_prompt_for_command = get_prompt_for_command
        self.files = files or {}


# Internal registry for bundled skills
_bundled_skills: dict[str, BundledSkillDefinition] = {}


def register_bundled_skill(definition: BundledSkillDefinition) -> None:
    """Register a bundled skill that will be available to the model.

    Bundled skills are compiled into the CLI binary and available to all users.
    """
    _bundled_skills[definition.name] = definition


def get_bundled_skill(name: str) -> Optional[BundledSkillDefinition]:
    """Get a bundled skill by name."""
    return _bundled_skills.get(name)


def get_all_bundled_skills() -> list[BundledSkillDefinition]:
    """Get all registered bundled skills.

    Returns a copy to prevent external mutation.
    """
    return list(_bundled_skills.values())


def clear_bundled_skills() -> None:
    """Clear bundled skills registry (for testing)."""
    _bundled_skills.clear()


def get_bundled_skills_root() -> str:
    """Get the root directory for bundled skill extraction."""
    # This would use a proper path in the actual implementation
    return os.path.join(os.path.expanduser('~'), '.cache', 'pyclaude', 'skills')


def is_ant_user() -> bool:
    """Check if the current user is an ant (internal user)."""
    return os.environ.get('USER_TYPE') == 'ant'


def is_auto_memory_enabled() -> bool:
    """Check if auto-memory is enabled."""
    try:
        from pyclaude.memdir.paths import isAutoMemoryEnabled
        return isAutoMemoryEnabled()
    except ImportError:
        return False


__all__ = [
    'BundledSkillDefinition',
    'register_bundled_skill',
    'get_bundled_skill',
    'get_all_bundled_skills',
    'clear_bundled_skills',
    'get_bundled_skills_root',
    'is_ant_user',
    'is_auto_memory_enabled',
]