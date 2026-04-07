"""Bundled Skills - Python implementation matching src/skills/bundled/"""
from __future__ import annotations

# Re-export from bundled_skills module
from pyclaude.skills.bundled_skills import (
    BundledSkillDefinition,
    register_bundled_skill,
    get_bundled_skill,
    get_all_bundled_skills,
    clear_bundled_skills,
    get_bundled_skills_root,
    is_ant_user,
    is_auto_memory_enabled,
    _bundled_skills as _internal_skills,
)

# BUNDLED_SKILLS is a reference to the internal dict for backwards compatibility
BUNDLED_SKILLS = _internal_skills


def init_bundled_skills() -> None:
    """Initialize all bundled skills."""
    # Import and register each skill
    from pyclaude.skills.bundled import (
        update_config,
        debug,
        keybindings,
        verify,
        lorem_ipsum,
        skillify,
        remember,
        simplify,
        batch,
        stuck,
        loop,
        schedule_remote_agents,
        claude_api,
        claude_in_chrome,
    )

    update_config.register()
    debug.register()
    keybindings.register()
    verify.register()
    lorem_ipsum.register()
    skillify.register()
    remember.register()
    simplify.register()
    batch.register()
    stuck.register()
    loop.register()
    schedule_remote_agents.register()
    claude_api.register()

    # claude-in-chrome is conditionally enabled based on Chrome setup
    claude_in_chrome.register()


# Auto-initialize on import
init_bundled_skills()


__all__ = [
    'BundledSkillDefinition',
    'BUNDLED_SKILLS',
    'register_bundled_skill',
    'get_bundled_skill',
    'get_all_bundled_skills',
    'init_bundled_skills',
    'is_ant_user',
    'is_auto_memory_enabled',
    'get_bundled_skills_root',
]