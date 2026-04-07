"""Skills command - manage skills."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILLS_DIR = Path.home() / '.claude' / 'skills'
SETTINGS_FILE = Path.home() / '.claude' / 'settings.json'


def load_settings() -> Dict[str, Any]:
    """Load settings from settings.json."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to settings.json."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def get_enabled_skills() -> Dict[str, bool]:
    """Get enabled skills from settings."""
    settings = load_settings()
    return settings.get('enabledSkills', {})


def set_skill_enabled(skill_name: str, enabled: bool) -> None:
    """Enable or disable a skill in settings."""
    settings = load_settings()
    if 'enabledSkills' not in settings:
        settings['enabledSkills'] = {}

    if enabled:
        settings['enabledSkills'][skill_name] = True
    else:
        if skill_name in settings['enabledSkills']:
            del settings['enabledSkills'][skill_name]

    save_settings(settings)


def parse_skill_args(args: str) -> Dict[str, Any]:
    """Parse skill command arguments."""
    args = args.strip().lower() if args else ''

    if not args or args == 'list':
        return {'type': 'list'}

    if args == 'installed':
        return {'type': 'list'}

    parts = args.split()
    command = parts[0] if parts else ''

    if command == 'enable':
        return {'type': 'enable', 'name': parts[1] if len(parts) > 1 else None}

    if command == 'disable':
        return {'type': 'disable', 'name': parts[1] if len(parts) > 1 else None}

    if command == 'help':
        return {'type': 'help'}

    return {'type': 'unknown'}


async def execute(args: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the skills command."""
    parsed = parse_skill_args(args)
    cmd_type = parsed.get('type')

    if cmd_type == 'list':
        return await list_skills()

    if cmd_type == 'enable':
        return await enable_skill(parsed.get('name', ''))

    if cmd_type == 'disable':
        return await disable_skill(parsed.get('name', ''))

    if cmd_type == 'help':
        return show_help()

    return show_help()


def show_help() -> Dict[str, Any]:
    """Show help message."""
    return {'type': 'text', 'value': '''Usage: /skills [command]

Commands:
  list              - List available skills
  enable <name>     - Enable a skill
  disable <name>    - Disable a skill
'''}


async def list_skills() -> Dict[str, Any]:
    """List available skills with enabled status."""
    enabled_skills = get_enabled_skills()
    skills = []

    # Load from user skills directory
    if SKILLS_DIR.exists():
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and (d / 'SKILL.md').exists():
                skills.append({
                    'name': d.name,
                    'path': str(d),
                    'enabled': d.name in enabled_skills or len(enabled_skills) == 0  # All enabled if no explicit config
                })

    if not skills:
        return {'type': 'text', 'value': 'No skills installed.\n\nSkills are stored in ~/.claude/skills/\nCreate a skill with: mkdir -p ~/.claude/skills/my-skill && echo "# SKILL.md" > ~/.claude/skills/my-skill/SKILL.md'}

    lines = ['Available skills:', '']
    for skill in sorted(skills, key=lambda s: s['name']):
        status = 'enabled' if skill['enabled'] else 'disabled'
        lines.append(f'  /{skill["name"]} ({status})')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def enable_skill(name: str) -> Dict[str, Any]:
    """Enable a skill."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /skills enable <name>'}

    # Check if skill exists
    skill_path = SKILLS_DIR / name
    if not skill_path.exists():
        return {'type': 'text', 'value': f'Skill "{name}" not found in ~/.claude/skills/'}

    set_skill_enabled(name, True)
    return {'type': 'text', 'value': f'Skill "{name}" enabled'}


async def disable_skill(name: str) -> Dict[str, Any]:
    """Disable a skill."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /skills disable <name>'}

    # Check if skill exists
    skill_path = SKILLS_DIR / name
    if not skill_path.exists():
        return {'type': 'text', 'value': f'Skill "{name}" not found in ~/.claude/skills/'}

    set_skill_enabled(name, False)
    return {'type': 'text', 'value': f'Skill "{name}" disabled'}


# Command metadata
CONFIG = {
    'type': 'local',
    'name': 'skills',
    'description': 'Manage skills',
    'supports_non_interactive': True,
}


call = execute