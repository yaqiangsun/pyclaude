"""Tests for plugins built-in registry."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from pyclaude.plugins import (
    BUILTIN_MARKETPLACE_NAME,
    LoadedPlugin,
    register_builtin_plugin,
    is_builtin_plugin_id,
    get_builtin_plugin_definition,
    get_builtin_plugins,
    get_builtin_plugin_skill_commands,
    clear_builtin_plugins,
)


class TestBUILTIN_MARKETPLACE_NAME:
    """Test builtin marketplace name constant."""

    def test_constant_value(self):
        """Test constant is 'builtin'."""
        assert BUILTIN_MARKETPLACE_NAME == 'builtin'


class TestRegisterBuiltinPlugin:
    """Test registering built-in plugins."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_builtin_plugins()

    def test_register_plugin(self):
        """Register a plugin."""
        definition = {
            'name': 'test-plugin',
            'description': 'Test plugin',
            'version': '1.0.0',
            'defaultEnabled': True,
        }
        register_builtin_plugin(definition)
        assert get_builtin_plugin_definition('test-plugin') == definition

    def test_register_multiple_plugins(self):
        """Register multiple plugins."""
        register_builtin_plugin({'name': 'plugin1', 'description': 'Plugin 1', 'version': '1.0.0'})
        register_builtin_plugin({'name': 'plugin2', 'description': 'Plugin 2', 'version': '1.0.0'})

        assert get_builtin_plugin_definition('plugin1') is not None
        assert get_builtin_plugin_definition('plugin2') is not None


class TestIsBuiltinPluginId:
    """Test checking if plugin ID is built-in."""

    def test_builtin_plugin_id(self):
        """Test builtin plugin ID."""
        assert is_builtin_plugin_id('my-plugin@builtin') is True

    def test_non_builtin_plugin_id(self):
        """Test non-builtin plugin ID."""
        assert is_builtin_plugin_id('my-plugin@marketplace') is False
        assert is_builtin_plugin_id('my-plugin') is False


class TestGetBuiltinPluginDefinition:
    """Test getting plugin definition."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_builtin_plugins()

    def test_get_existing_plugin(self):
        """Get existing plugin."""
        definition = {'name': 'test', 'description': 'Test', 'version': '1.0.0'}
        register_builtin_plugin(definition)
        result = get_builtin_plugin_definition('test')
        assert result == definition

    def test_get_nonexistent_plugin(self):
        """Get nonexistent plugin."""
        result = get_builtin_plugin_definition('nonexistent')
        assert result is None


class TestGetBuiltinPlugins:
    """Test getting all built-in plugins."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_builtin_plugins()

    def test_empty_registry(self):
        """Empty registry returns empty lists."""
        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            assert result['enabled'] == []
            assert result['disabled'] == []

    def test_returns_loaded_plugins(self):
        """Returns LoadedPlugin objects."""
        register_builtin_plugin({
            'name': 'test-plugin',
            'description': 'Test plugin',
            'version': '1.0.0',
            'defaultEnabled': True,
        })

        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            assert len(result['enabled']) == 1
            plugin = result['enabled'][0]
            assert isinstance(plugin, LoadedPlugin)
            assert plugin.name == 'test-plugin'
            assert plugin.is_builtin is True

    def test_respects_default_enabled(self):
        """Respects defaultEnabled field."""
        register_builtin_plugin({
            'name': 'enabled-plugin',
            'description': 'Enabled',
            'version': '1.0.0',
            'defaultEnabled': True,
        })
        register_builtin_plugin({
            'name': 'disabled-plugin',
            'description': 'Disabled',
            'version': '1.0.0',
            'defaultEnabled': False,
        })

        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            enabled_names = [p.name for p in result['enabled']]
            disabled_names = [p.name for p in result['disabled']]

            assert 'enabled-plugin' in enabled_names
            assert 'disabled-plugin' in disabled_names

    def test_user_setting_overrides_default(self):
        """User setting overrides defaultEnabled."""
        register_builtin_plugin({
            'name': 'test-plugin',
            'description': 'Test',
            'version': '1.0.0',
            'defaultEnabled': False,  # Default disabled
        })

        # User enables it
        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={'test-plugin@builtin': True}):
            result = get_builtin_plugins()
            enabled_names = [p.name for p in result['enabled']]
            assert 'test-plugin' in enabled_names

    def test_respects_is_available(self):
        """Respects isAvailable check."""
        # Plugin with availability check
        register_builtin_plugin({
            'name': 'available-plugin',
            'description': 'Available',
            'version': '1.0.0',
            'isAvailable': lambda: True,
        })
        register_builtin_plugin({
            'name': 'unavailable-plugin',
            'description': 'Unavailable',
            'version': '1.0.0',
            'isAvailable': lambda: False,
        })

        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            names = [p.name for p in result['enabled']]

            assert 'available-plugin' in names
            assert 'unavailable-plugin' not in names

    def test_includes_hooks_config(self):
        """Includes hooks config."""
        register_builtin_plugin({
            'name': 'test-plugin',
            'description': 'Test',
            'version': '1.0.0',
            'hooks': {'prePrompt': ['some-hook']},
        })

        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            plugin = result['enabled'][0]
            assert plugin.hooks_config == {'prePrompt': ['some-hook']}

    def test_includes_mcp_servers(self):
        """Includes MCP servers config."""
        register_builtin_plugin({
            'name': 'test-plugin',
            'description': 'Test',
            'version': '1.0.0',
            'mcpServers': [{'name': 'mcp1', 'command': 'npx'}],
        })

        with patch('pyclaude.plugins._load_enabled_plugins_from_settings', return_value={}):
            result = get_builtin_plugins()
            plugin = result['enabled'][0]
            assert plugin.mcp_servers == [{'name': 'mcp1', 'command': 'npx'}]


class TestLoadedPlugin:
    """Test LoadedPlugin dataclass."""

    def test_creation(self):
        """Create a LoadedPlugin."""
        plugin = LoadedPlugin(
            name='test',
            manifest={'name': 'test', 'description': 'Test', 'version': '1.0.0'},
            path='builtin',
            source='test@builtin',
            repository='test@builtin',
            enabled=True,
            is_builtin=True,
        )
        assert plugin.name == 'test'
        assert plugin.enabled is True
        assert plugin.is_builtin is True


class TestGetBuiltinPluginSkillCommands:
    """Test getting skill commands from plugins."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_builtin_plugins()

    def test_returns_empty_list(self):
        """Returns empty list (not implemented)."""
        result = get_builtin_plugin_skill_commands()
        assert result == []


class TestClearBuiltinPlugins:
    """Test clearing plugin registry."""

    def test_clear_removes_all(self):
        """Clear removes all plugins."""
        register_builtin_plugin({'name': 'test', 'description': 'Test', 'version': '1.0.0'})
        clear_builtin_plugins()
        assert get_builtin_plugin_definition('test') is None