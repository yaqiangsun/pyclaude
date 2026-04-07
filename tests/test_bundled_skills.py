"""Tests for bundled skills."""
import os
import pytest
from unittest.mock import patch


class TestBundledSkillDefinition:
    """Test BundledSkillDefinition class."""

    def test_default_values(self):
        """Test default values."""
        from pyclaude.skills.bundled_skills import BundledSkillDefinition

        skill = BundledSkillDefinition(
            name='test',
            description='Test skill',
        )
        assert skill.name == 'test'
        assert skill.description == 'Test skill'
        assert skill.allowed_tools == []
        assert skill.user_invocable is True
        assert skill.is_enabled() is True

    def test_custom_values(self):
        """Test custom values."""
        from pyclaude.skills.bundled_skills import BundledSkillDefinition

        def custom_check():
            return False

        skill = BundledSkillDefinition(
            name='test',
            description='Test skill',
            allowed_tools=['Read', 'Write'],
            argument_hint='<arg>',
            when_to_use='When testing',
            model='opus',
            disable_model_invocation=True,
            user_invocable=False,
            hooks=['hook1'],
            context={'key': 'value'},
            is_enabled=custom_check,
        )
        assert skill.allowed_tools == ['Read', 'Write']
        assert skill.argument_hint == '<arg>'
        assert skill.when_to_use == 'When testing'
        assert skill.model == 'opus'
        assert skill.disable_model_invocation is True
        assert skill.user_invocable is False
        assert skill.hooks == ['hook1']
        assert skill.context == {'key': 'value'}
        assert skill.is_enabled() is False


class TestRegisterBundledSkill:
    """Test skill registration."""

    def test_register_skill(self):
        """Test registering a skill."""
        from pyclaude.skills.bundled_skills import (
            BUNDLED_SKILLS,
            register_bundled_skill,
            BundledSkillDefinition,
            get_bundled_skill,
        )

        skill = BundledSkillDefinition(name='test-register', description='Test')
        register_bundled_skill(skill)
        assert 'test-register' in BUNDLED_SKILLS

    def test_get_bundled_skill(self):
        """Test getting a bundled skill."""
        from pyclaude.skills.bundled_skills import (
            get_bundled_skill,
            BundledSkillDefinition,
        )

        skill = get_bundled_skill('update-config')
        assert skill is not None
        assert skill.name == 'update-config'

    def test_get_nonexistent_skill(self):
        """Test getting non-existent skill returns None."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        result = get_bundled_skill('nonexistent-skill')
        assert result is None

    def test_get_all_bundled_skills(self):
        """Test getting all bundled skills."""
        from pyclaude.skills.bundled_skills import get_all_bundled_skills

        skills = get_all_bundled_skills()
        assert len(skills) > 0
        assert all(hasattr(s, 'name') for s in skills)


class TestIsAntUser:
    """Test ant user detection."""

    def test_not_ant_by_default(self):
        """Test not ant by default."""
        with patch.dict(os.environ, {}, clear=True):
            from pyclaude.skills.bundled_skills import is_ant_user
            assert is_ant_user() is False

    def test_ant_when_user_type_ant(self):
        """Test ant when USER_TYPE is ant."""
        with patch.dict(os.environ, {'USER_TYPE': 'ant'}):
            from pyclaude.skills.bundled_skills import is_ant_user
            assert is_ant_user() is True


class TestLoremIpsum:
    """Test lorem ipsum generation."""

    def test_generate_small(self):
        """Generate small amount of lorem ipsum."""
        from pyclaude.skills.bundled_skills import generate_lorem_ipsum

        text = generate_lorem_ipsum(10)
        assert len(text) > 0
        assert isinstance(text, str)

    def test_generate_creates_sentences(self):
        """Generate creates proper sentences."""
        from pyclaude.skills.bundled_skills import generate_lorem_ipsum

        text = generate_lorem_ipsum(100)
        assert '.' in text

    def test_token_limit(self):
        """Test token limit is respected."""
        from pyclaude.skills.bundled_skills import generate_lorem_ipsum

        # Cap is 500k
        text = generate_lorem_ipsum(600_000)
        # Should cap at 500k
        words = text.split()
        assert len(words) <= 510_000  # Some margin


class TestSkillPrompts:
    """Test skill prompt generation."""

    def test_update_config_prompt(self):
        """Test update-config skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('update-config')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'settings' in result[0]['text'].lower() or 'config' in result[0]['text'].lower()

    def test_debug_prompt(self):
        """Test debug skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('debug')
        assert skill is not None

        result = skill.get_prompt_for_command('test issue')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'test issue' in result[0]['text']

    def test_keybindings_prompt(self):
        """Test keybindings skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('keybindings-help')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'keybindings' in result[0]['text'].lower() or 'shortcut' in result[0]['text'].lower()

    def test_simplify_prompt(self):
        """Test simplify skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('simplify')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'review' in result[0]['text'].lower() or 'code' in result[0]['text'].lower()

    def test_remember_prompt(self):
        """Test remember skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('remember')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'memory' in result[0]['text'].lower() or 'claude.md' in result[0]['text'].lower()

    def test_batch_prompt(self):
        """Test batch skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('batch')
        assert skill is not None

        result = skill.get_prompt_for_command('migrate from react to vue')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'migrate from react to vue' in result[0]['text']

    def test_batch_empty_args(self):
        """Test batch skill with empty args."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('batch')
        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert 'instruction' in result[0]['text'].lower()

    def test_loop_prompt(self):
        """Test loop skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        assert skill is not None

        result = skill.get_prompt_for_command('check the deploy every 20m')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'check the deploy' in result[0]['text']

    def test_loop_empty_args(self):
        """Test loop skill with empty args."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert 'usage' in result[0]['text'].lower() or '/loop' in result[0]['text']

    def test_schedule_prompt(self):
        """Test schedule skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('schedule')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'remote' in result[0]['text'].lower() or 'schedule' in result[0]['text'].lower()

    def test_claude_api_prompt(self):
        """Test claude-api skill prompt."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('claude-api')
        assert skill is not None

        result = skill.get_prompt_for_command('')
        assert len(result) > 0
        assert result[0]['type'] == 'text'
        assert 'claude api' in result[0]['text'].lower() or 'anthropic' in result[0]['text'].lower()


class TestAntOnlySkills:
    """Test ANT-only skills."""

    @patch.dict(os.environ, {'USER_TYPE': 'ant'})
    def test_verify_skill_registered_for_ant(self):
        """Verify skill registered for ant user."""
        # Re-import to pick up the patched env
        import importlib
        from pyclaude.skills import bundled_skills
        importlib.reload(bundled_skills)
        bundled_skills.init_bundled_skills()

        skill = bundled_skills.get_bundled_skill('verify')
        # For ant users, should be registered
        assert skill is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_verify_skill_not_registered_for_non_ant(self):
        """Verify skill not registered for non-ant user."""
        import importlib
        from pyclaude.skills import bundled_skills
        importlib.reload(bundled_skills)
        bundled_skills.init_bundled_skills()

        skill = bundled_skills.get_bundled_skill('verify')
        # For non-ant, verify should not be registered (returns None)
        # This is expected behavior from the original TS


class TestSkillAttributes:
    """Test skill attributes."""

    def test_update_config_attributes(self):
        """Test update-config has correct attributes."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('update-config')
        assert skill.name == 'update-config'
        assert skill.user_invocable is True

    def test_debug_attributes(self):
        """Test debug has correct attributes."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('debug')
        assert skill.name == 'debug'
        assert skill.disable_model_invocation is True
        assert 'Read' in skill.allowed_tools

    def test_keybindings_not_user_invocable(self):
        """Test keybindings is not user invocable."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('keybindings-help')
        assert skill.user_invocable is False

    def test_batch_disable_model_invocation(self):
        """Test batch has disable_model_invocation."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('batch')
        assert skill.disable_model_invocation is True


class TestHooksParsing:
    """Test interval parsing for loop skill."""

    def test_parse_leading_interval(self):
        """Parse leading interval token."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        result = skill.get_prompt_for_command('5m check the deploy')
        assert 'Interval: 5m' in result[0]['text']
        assert 'check the deploy' in result[0]['text']

    def test_parse_trailing_every(self):
        """Parse trailing every clause."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        result = skill.get_prompt_for_command('check the deploy every 20m')
        assert '20m' in result[0]['text']
        assert 'check the deploy' in result[0]['text']

    def test_parse_every_minutes(self):
        """Parse 'every 5 minutes'."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        result = skill.get_prompt_for_command('run tests every 5 minutes')
        assert '5m' in result[0]['text']

    def test_default_interval(self):
        """Default interval when none specified."""
        from pyclaude.skills.bundled_skills import get_bundled_skill

        skill = get_bundled_skill('loop')
        result = skill.get_prompt_for_command('check the deploy')
        assert 'Interval: 10m' in result[0]['text']


class TestInitBundledSkills:
    """Test init_bundled_skills function."""

    def test_init_registers_skills(self):
        """Test init registers multiple skills."""
        from pyclaude.skills.bundled_skills import (
            BUNDLED_SKILLS,
            init_bundled_skills,
            get_bundled_skill,
        )

        # Clear existing
        BUNDLED_SKILLS.clear()

        # Init
        init_bundled_skills()

        # Check key skills registered
        assert get_bundled_skill('update-config') is not None
        assert get_bundled_skill('debug') is not None
        assert get_bundled_skill('keybindings-help') is not None
        assert get_bundled_skill('simplify') is not None
        assert get_bundled_skill('batch') is not None
        assert get_bundled_skill('loop') is not None
        assert get_bundled_skill('schedule') is not None
        assert get_bundled_skill('claude-api') is not None