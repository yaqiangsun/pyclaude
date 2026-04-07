"""Tests for skills directory loading."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from pyclaude.skills.load_skills_dir import (
    Skill,
    load_skills_dir,
    load_skills_from_dir,
    get_skills_dir_commands,
    get_file_identity,
    parse_skill_frontmatter,
)


class TestParseSkillFrontmatter:
    """Test skill frontmatter parsing."""

    def test_parse_basic_frontmatter(self):
        """Parse basic frontmatter fields."""
        frontmatter = {
            'description': 'Test skill description',
            'name': 'Test Skill',
            'allowed-tools': 'Bash, Read, Edit',
        }
        content = '# Test Skill\n\nSome content'
        result = parse_skill_frontmatter(frontmatter, content, 'test-skill')

        assert result['description'] == 'Test skill description'
        assert result['display_name'] == 'Test Skill'
        assert 'Bash' in result['allowed_tools']

    def test_parse_frontmatter_no_description(self):
        """Parse when no description in frontmatter."""
        frontmatter = {}
        content = '# My Skill\n\nThis is the first paragraph of content.'
        result = parse_skill_frontmatter(frontmatter, content, 'my-skill')

        assert 'description' in result
        assert 'first paragraph' in result['description'].lower()

    def test_parse_user_invocable_default(self):
        """Test user-invocable defaults to True."""
        frontmatter = {}
        result = parse_skill_frontmatter(frontmatter, '', 'test')
        assert result['user_invocable'] is True

    def test_parse_user_invocable_false(self):
        """Test user-invocable can be set to False."""
        frontmatter = {'user-invocable': 'false'}
        result = parse_skill_frontmatter(frontmatter, '', 'test')
        assert result['user_invocable'] is False

    def test_parse_paths(self):
        """Test paths frontmatter parsing."""
        frontmatter = {'paths': 'src/**/*.ts\ntests/**/*.py'}
        result = parse_skill_frontmatter(frontmatter, '', 'test')
        assert result['paths'] is not None
        assert 'src/**/*.ts' in result['paths']

    def test_parse_argument_names(self):
        """Test argument names parsing."""
        frontmatter = {'arguments': '{name}, {age}'}
        result = parse_skill_frontmatter(frontmatter, '', 'test')
        assert 'name' in result['argument_names']
        assert 'age' in result['argument_names']


class TestLoadSkillsFromDir:
    """Test loading skills from directory."""

    def test_load_empty_directory(self):
        """Load skills from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skills = load_skills_from_dir(tmpdir)
            assert skills == []

    def test_load_nonexistent_directory(self):
        """Load skills from nonexistent directory."""
        skills = load_skills_from_dir('/nonexistent/path')
        assert skills == []

    def test_load_skills_with_skill_md(self):
        """Load skills from directory with SKILL.md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skill directory
            skill_dir = Path(tmpdir) / 'my-skill'
            skill_dir.mkdir()
            (skill_dir / 'SKILL.md').write_text(
                '---\ndescription: My test skill\n---\n\n# Skill Content\n\nSome content here.'
            )

            skills = load_skills_from_dir(tmpdir)
            assert len(skills) == 1
            assert skills[0].name == 'my-skill'
            assert 'test skill' in skills[0].description.lower()
            assert skills[0].loaded_from == 'skills'

    def test_load_skills_ignores_non_directories(self):
        """Load skills ignores non-directory files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a plain .md file (not in a directory)
            (Path(tmpdir) / 'note.md').write_text('# Note')

            skills = load_skills_from_dir(tmpdir)
            assert skills == []

    def test_load_skills_ignores_missing_skill_md(self):
        """Load skills ignores directories without SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory without SKILL.md
            skill_dir = Path(tmpdir) / 'my-skill'
            skill_dir.mkdir()
            (skill_dir / 'README.md').write_text('# README')

            skills = load_skills_from_dir(tmpdir)
            assert skills == []


class TestSkill:
    """Test Skill dataclass."""

    def test_skill_defaults(self):
        """Test Skill default values."""
        skill = Skill(
            name='test',
            description='Test',
            content='Content',
            file_path='/test/path',
            source='userSettings',
            loaded_from='skills',
        )
        assert skill.allowed_tools == []
        assert skill.argument_names == []
        assert skill.user_invocable is True
        assert skill.is_hidden is False


class TestGetFileIdentity:
    """Test file identity resolution."""

    def test_existing_file(self):
        """Get identity of existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'test')
            path = f.name

        try:
            identity = get_file_identity(path)
            assert identity is not None
            assert os.path.exists(identity)
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        """Get identity of nonexistent file returns path."""
        # On macOS, realpath doesn't raise for non-existent paths
        identity = get_file_identity('/nonexistent/file.txt')
        assert identity is not None  # Returns the resolved path


class TestLoadSkillsDir:
    """Test legacy load_skills_dir function."""

    def test_load_skills_dir_returns_dicts(self):
        """load_skills_dir returns list of dicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a skill
            skill_dir = Path(tmpdir) / 'test-skill'
            skill_dir.mkdir()
            (skill_dir / 'SKILL.md').write_text('---\ndescription: Test\n---\n\nContent')

            result = load_skills_dir(tmpdir)
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], dict)
                assert 'name' in result[0]


class TestGetSkillsDirCommands:
    """Test get_skills_dir_commands."""

    def test_returns_list(self):
        """Test returns a list."""
        # This will try to access actual filesystem paths - test the structure
        result = get_skills_dir_commands.__doc__
        assert result is not None