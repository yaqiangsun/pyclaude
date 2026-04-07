"""Tests for skills command."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pyclaude.commands.skills.skills import (
    parse_skill_args,
    get_enabled_skills,
    set_skill_enabled,
    load_settings,
    save_settings,
)


class TestParseSkillArgs:
    """Test skill argument parsing."""

    def test_empty_args_returns_list(self):
        """Empty args returns list type."""
        result = parse_skill_args("")
        assert result['type'] == 'list'

    def test_list_command(self):
        """Parse list command."""
        result = parse_skill_args("list")
        assert result['type'] == 'list'

    def test_installed_command(self):
        """Parse installed command."""
        result = parse_skill_args("installed")
        assert result['type'] == 'list'

    def test_enable_command(self):
        """Parse enable command."""
        result = parse_skill_args("enable my-skill")
        assert result['type'] == 'enable'
        assert result['name'] == 'my-skill'

    def test_disable_command(self):
        """Parse disable command."""
        result = parse_skill_args("disable my-skill")
        assert result['type'] == 'disable'
        assert result['name'] == 'my-skill'

    def test_help_command(self):
        """Parse help command."""
        result = parse_skill_args("help")
        assert result['type'] == 'help'

    def test_unknown_command(self):
        """Unknown command returns unknown type."""
        result = parse_skill_args("unknown")
        assert result['type'] == 'unknown'


class TestSkillSettings:
    """Test skill settings management."""

    @patch('pyclaude.commands.skills.skills.SETTINGS_FILE')
    def test_get_enabled_skills_empty(self, mock_settings_file):
        """Get enabled skills returns empty dict when no settings."""
        mock_settings_file.exists.return_value = False
        result = get_enabled_skills()
        assert result == {}

    @patch('pyclaude.commands.skills.skills.SETTINGS_FILE')
    def test_get_enabled_skills_with_data(self, mock_settings_file):
        """Get enabled skills returns enabled skills."""
        mock_settings_file.exists.return_value = True
        mock_open = patch('pyclaude.commands.skills.skills.open', MagicMock())
        with mock_open as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = json.dumps({
                'enabledSkills': {'skill1': True, 'skill2': True}
            })
            result = get_enabled_skills()
            assert result == {'skill1': True, 'skill2': True}

    @patch('pyclaude.commands.skills.skills.SETTINGS_FILE')
    @patch('pyclaude.commands.skills.skills.save_settings')
    def test_set_skill_enabled_true(self, mock_save, mock_settings_file):
        """Enable a skill."""
        mock_settings_file.exists.return_value = True
        with patch('pyclaude.commands.skills.skills.open', MagicMock()) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = json.dumps({})
            set_skill_enabled('my-skill', True)
            mock_save.assert_called_once()
            # Check enabledSkills was set
            call_args = mock_save.call_args[0][0]
            assert 'enabledSkills' in call_args
            assert call_args['enabledSkills'].get('my-skill') is True

    @patch('pyclaude.commands.skills.skills.SETTINGS_FILE')
    @patch('pyclaude.commands.skills.skills.save_settings')
    def test_set_skill_enabled_false(self, mock_save, mock_settings_file):
        """Disable a skill."""
        mock_settings_file.exists.return_value = True
        with patch('pyclaude.commands.skills.skills.open', MagicMock()) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = json.dumps({
                'enabledSkills': {'skill1': True, 'skill2': True}
            })
            set_skill_enabled('skill1', False)
            mock_save.assert_called_once()
            # Check skill was removed
            call_args = mock_save.call_args[0][0]
            assert 'skill1' not in call_args.get('enabledSkills', {})


class TestSkillArgsEdgeCases:
    """Test edge cases in skill argument parsing."""

    def test_enable_no_name(self):
        """Enable with no skill name returns enable type with None name."""
        result = parse_skill_args("enable")
        assert result['type'] == 'enable'
        assert result.get('name') is None

    def test_disable_no_name(self):
        """Disable with no skill name returns disable type with None name."""
        result = parse_skill_args("disable")
        assert result['type'] == 'disable'
        assert result.get('name') is None

    def test_uppercase_args(self):
        """Args are lowercased."""
        result = parse_skill_args("ENABLE My-Skill")
        assert result['type'] == 'enable'
        assert result['name'] == 'my-skill'

    def test_extra_spaces(self):
        """Extra spaces are handled."""
        result = parse_skill_args("  enable   my-skill  ")
        assert result['type'] == 'enable'
        assert result['name'] == 'my-skill'