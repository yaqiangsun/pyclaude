"""Load Skills Directory."""
from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pyclaude.utils.frontmatter_parser import parse_frontmatter

# Memory types for skills
MEMORY_TYPES = ['user', 'feedback', 'project', 'reference']


@dataclass
class Skill:
    """Represents a loaded skill."""
    name: str
    description: str
    content: str
    file_path: str
    source: str
    loaded_from: str
    display_name: Optional[str] = None
    allowed_tools: list = None
    argument_hint: Optional[str] = None
    argument_names: list = None
    when_to_use: Optional[str] = None
    version: Optional[str] = None
    user_invocable: bool = True
    is_hidden: bool = False
    paths: Optional[list] = None

    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = []
        if self.argument_names is None:
            self.argument_names = []


def get_file_identity(file_path: str) -> Optional[str]:
    """Get a unique identifier for a file by resolving symlinks.

    Returns None if the file doesn't exist or can't be resolved.
    """
    try:
        return os.path.realpath(file_path)
    except OSError:
        return None


def parse_skill_frontmatter(frontmatter: dict, content: str, name: str) -> dict:
    """Parse skill frontmatter fields."""
    result = {}

    # Description - from frontmatter or extracted from content
    if frontmatter and 'description' in frontmatter:
        result['description'] = frontmatter['description']
    else:
        # Extract first paragraph as description
        lines = content.strip().split('\n')
        description = ''
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                description = line[:100]  # First 100 chars
                break
        result['description'] = description or f'{name} skill'

    # displayName
    if frontmatter and 'name' in frontmatter:
        result['display_name'] = str(frontmatter['name'])

    # allowedTools
    if frontmatter and 'allowed-tools' in frontmatter:
        tools_str = frontmatter['allowed-tools']
        if isinstance(tools_str, str):
            result['allowed_tools'] = [t.strip() for t in tools_str.split(',')]
        elif isinstance(tools_str, list):
            result['allowed_tools'] = tools_str
        else:
            result['allowed_tools'] = []
    else:
        result['allowed_tools'] = []

    # argumentHint
    if frontmatter and 'argument-hint' in frontmatter:
        result['argument_hint'] = str(frontmatter['argument-hint'])

    # argumentNames (from 'arguments' field)
    if frontmatter and 'arguments' in frontmatter:
        args_str = frontmatter['arguments']
        if isinstance(args_str, str):
            result['argument_names'] = [a.strip().strip('{}') for a in args_str.split(',')]
        elif isinstance(args_str, list):
            result['argument_names'] = [str(a).strip().strip('{}') for a in args_str]
        else:
            result['argument_names'] = []
    else:
        result['argument_names'] = []

    # whenToUse
    if frontmatter and 'when_to_use' in frontmatter:
        result['when_to_use'] = frontmatter['when_to_use']

    # version
    if frontmatter and 'version' in frontmatter:
        result['version'] = str(frontmatter['version'])

    # userInvocable - defaults to True
    if frontmatter and 'user-invocable' in frontmatter:
        val = frontmatter['user-invocable']
        result['user_invocable'] = str(val).lower() not in ('false', '0', 'no')
    else:
        result['user_invocable'] = True

    # paths (conditional skills)
    if frontmatter and 'paths' in frontmatter:
        paths_str = frontmatter['paths']
        if isinstance(paths_str, str):
            result['paths'] = [p.strip() for p in paths_str.split('\n') if p.strip()]
        elif isinstance(paths_str, list):
            result['paths'] = [str(p) for p in paths_str]
        else:
            result['paths'] = None
    else:
        result['paths'] = None

    return result


def load_skills_from_dir(base_path: str, source: str = 'userSettings') -> list[Skill]:
    """Load skills from a directory.

    Supports directory format: skill-name/SKILL.md

    Args:
        base_path: Path to the skills directory
        source: Setting source (userSettings, projectSettings, policySettings)

    Returns:
        List of loaded skills
    """
    skills = []
    skills_path = Path(base_path)

    if not skills_path.exists():
        return skills

    if not skills_path.is_dir():
        return skills

    try:
        entries = list(skills_path.iterdir())
    except PermissionError:
        return skills

    for entry in entries:
        # Only support directory format: skill-name/SKILL.md
        if not entry.is_dir():
            continue

        skill_file_path = entry / 'SKILL.md'

        if not skill_file_path.exists():
            continue

        try:
            content = skill_file_path.read_text(encoding='utf-8')
        except (PermissionError, OSError):
            continue

        # Parse frontmatter
        frontmatter, markdown_content = parse_frontmatter(content)

        skill_name = entry.name

        # Parse frontmatter fields
        parsed = parse_skill_frontmatter(frontmatter or {}, markdown_content, skill_name)

        skill = Skill(
            name=skill_name,
            description=parsed.get('description', f'{skill_name} skill'),
            content=markdown_content,
            file_path=str(skill_file_path),
            source=source,
            loaded_from='skills',
            display_name=parsed.get('display_name'),
            allowed_tools=parsed.get('allowed_tools', []),
            argument_hint=parsed.get('argument_hint'),
            argument_names=parsed.get('argument_names', []),
            when_to_use=parsed.get('when_to_use'),
            version=parsed.get('version'),
            user_invocable=parsed.get('user_invocable', True),
            is_hidden=not parsed.get('user_invocable', True),
            paths=parsed.get('paths'),
        )
        skills.append(skill)

    return skills


def load_skills_dir(skills_dir: str | Path) -> list[dict[str, Any]]:
    """Load skills from a directory.

    Returns a list of skill dictionaries (legacy format for compatibility).

    Args:
        skills_dir: Path to the skills directory

    Returns:
        List of skill dictionaries
    """
    if isinstance(skills_dir, str):
        skills_dir = Path(skills_dir)

    skills = load_skills_from_dir(str(skills_dir))

    # Convert to legacy dict format
    return [
        {
            'name': s.name,
            'description': s.description,
            'content': s.content,
            'path': s.file_path,
            'source': s.source,
            'loaded_from': s.loaded_from,
        }
        for s in skills
    ]


def get_skills_dir_commands(cwd: str = None) -> list[Skill]:
    """Load all skills from all configured directories.

    Loads from:
    - User skills: ~/.claude/skills
    - Project skills: .claude/skills in cwd and parents
    - Managed skills: ~/.claude-managed/.claude/skills

    Args:
        cwd: Current working directory for project skills

    Returns:
        List of all loaded skills
    """
    from pyclaude.utils.env_utils import get_claude_config_home_dir, get_managed_file_path

    all_skills = []
    seen_paths = set()

    # User skills
    user_skills_dir = Path(get_claude_config_home_dir()) / 'skills'
    user_skills = load_skills_from_dir(str(user_skills_dir), 'userSettings')

    # Deduplicate by resolved path
    for skill in user_skills:
        file_id = get_file_identity(skill.file_path)
        if file_id and file_id not in seen_paths:
            seen_paths.add(file_id)
            all_skills.append(skill)

    # Managed skills
    managed_skills_dir = Path(get_managed_file_path()) / '.claude' / 'skills'
    managed_skills = load_skills_from_dir(str(managed_skills_dir), 'policySettings')

    for skill in managed_skills:
        file_id = get_file_identity(skill.file_path)
        if file_id and file_id not in seen_paths:
            seen_paths.add(file_id)
            all_skills.append(skill)

    # Project skills (if cwd provided)
    if cwd:
        project_skills = load_project_skills(cwd)
        for skill in project_skills:
            file_id = get_file_identity(skill.file_path)
            if file_id and file_id not in seen_paths:
                seen_paths.add(file_id)
                all_skills.append(skill)

    return all_skills


def load_project_skills(cwd: str) -> list[Skill]:
    """Load skills from project .claude/skills directories.

    Walks up from cwd to home directory, loading .claude/skills from each level.
    """
    from pyclaude.utils.env_utils import get_project_dirs_up_to_home

    skills = []
    project_dirs = get_project_dirs_up_to_home('skills', cwd)

    for project_dir in project_dirs:
        project_skills_dir = Path(project_dir) / '.claude' / 'skills'
        project_skills = load_skills_from_dir(str(project_skills_dir), 'projectSettings')
        skills.extend(project_skills)

    return skills


__all__ = [
    'Skill',
    'load_skills_dir',
    'load_skills_from_dir',
    'get_skills_dir_commands',
    'load_project_skills',
    'get_file_identity',
    'parse_skill_frontmatter',
]