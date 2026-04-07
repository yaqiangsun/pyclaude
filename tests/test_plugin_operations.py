"""Tests for plugin operations."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pyclaude.services.plugins.plugin_operations import (
    PluginOperationResult,
    PluginUpdateResult,
    VALID_INSTALLABLE_SCOPES,
    VALID_UPDATE_SCOPES,
    get_settings_file_path,
)
from pyclaude.commands.plugins.plugins import parse_plugin_args


class TestValidScopes:
    """Test scope constants."""

    def test_valid_installable_scopes(self):
        """Valid installable scopes are defined."""
        assert "user" in VALID_INSTALLABLE_SCOPES
        assert "project" in VALID_INSTALLABLE_SCOPES
        assert "local" in VALID_INSTALLABLE_SCOPES

    def test_valid_update_scopes(self):
        """Valid update scopes include managed."""
        assert "user" in VALID_UPDATE_SCOPES
        assert "project" in VALID_UPDATE_SCOPES
        assert "local" in VALID_UPDATE_SCOPES
        assert "managed" in VALID_UPDATE_SCOPES


class TestSettingsManagement:
    """Test settings file operations."""

    @patch('pyclaude.services.plugins.plugin_operations.get_plugins_directory')
    def test_get_settings_file_path_user(self, mock_get_dir):
        """Get user settings file path."""
        mock_get_dir.return_value = Path.home() / '.claude' / 'plugins'
        path = get_settings_file_path('user')
        assert path.name == 'settings.json'
        assert '.claude' in str(path)

    def test_get_settings_file_path_local(self):
        """Get local settings file path."""
        path = get_settings_file_path('local')
        assert path.name == 'settings.json'
        assert '.claude' in str(path)


class TestParsePluginArgs:
    """Test plugin argument parsing."""

    def test_empty_args_returns_menu(self):
        """Empty args returns menu type."""
        result = parse_plugin_args("")
        assert result['type'] == 'menu'

    def test_parse_install_command(self):
        """Parse install command."""
        result = parse_plugin_args("install my-plugin")
        assert result['type'] == 'install'
        assert result['plugin'] == 'my-plugin'

    def test_parse_install_command_alias(self):
        """Parse install alias 'i'."""
        result = parse_plugin_args("i my-plugin")
        assert result['type'] == 'install'
        assert result['plugin'] == 'my-plugin'

    def test_parse_install_with_marketplace(self):
        """Parse plugin@marketplace format."""
        result = parse_plugin_args("install my-plugin@my-marketplace")
        assert result['type'] == 'install'
        assert result['plugin'] == 'my-plugin'
        assert result['marketplace'] == 'my-marketplace'

    def test_parse_uninstall_command(self):
        """Parse uninstall command."""
        result = parse_plugin_args("uninstall my-plugin")
        assert result['type'] == 'uninstall'
        assert result['plugin'] == 'my-plugin'

    def test_parse_enable_command(self):
        """Parse enable command."""
        result = parse_plugin_args("enable my-plugin")
        assert result['type'] == 'enable'
        assert result['plugin'] == 'my-plugin'

    def test_parse_disable_command(self):
        """Parse disable command."""
        result = parse_plugin_args("disable my-plugin")
        assert result['type'] == 'disable'
        assert result['plugin'] == 'my-plugin'

    def test_parse_disable_all(self):
        """Parse disable --all command."""
        result = parse_plugin_args("disable --all")
        assert result['type'] == 'disable'
        assert result['all'] is True

    def test_parse_disable_all_alias(self):
        """Parse disable -a command."""
        result = parse_plugin_args("disable -a")
        assert result['type'] == 'disable'
        assert result['all'] is True

    def test_parse_update_command(self):
        """Parse update command."""
        result = parse_plugin_args("update my-plugin")
        assert result['type'] == 'update'
        assert result['plugin'] == 'my-plugin'

    def test_parse_validate_command(self):
        """Parse validate command."""
        result = parse_plugin_args("validate /path/to/plugin")
        assert result['type'] == 'validate'
        assert result['path'] == '/path/to/plugin'

    def test_parse_marketplace_add(self):
        """Parse marketplace add command."""
        result = parse_plugin_args("marketplace add github:owner/repo")
        assert result['type'] == 'marketplace'
        assert result['action'] == 'add'
        assert result['target'] == 'github:owner/repo'

    def test_parse_marketplace_remove(self):
        """Parse marketplace remove command."""
        result = parse_plugin_args("marketplace remove my-marketplace")
        assert result['type'] == 'marketplace'
        assert result['action'] == 'remove'
        assert result['target'] == 'my-marketplace'

    def test_parse_marketplace_list(self):
        """Parse marketplace list command."""
        result = parse_plugin_args("marketplace list")
        assert result['type'] == 'marketplace'
        assert result['action'] == 'list'

    def test_parse_marketplace_update(self):
        """Parse marketplace update command."""
        result = parse_plugin_args("marketplace update")
        assert result['type'] == 'marketplace'
        assert result['action'] == 'update'

    def test_parse_list_command(self):
        """Parse list command."""
        result = parse_plugin_args("list")
        assert result['type'] == 'list'

    def test_parse_help_command(self):
        """Parse help command."""
        result = parse_plugin_args("help")
        assert result['type'] == 'help'

    def test_parse_manage_command(self):
        """Parse manage command."""
        result = parse_plugin_args("manage")
        assert result['type'] == 'manage'


class TestPluginOperationResult:
    """Test plugin operation result dataclass."""

    def test_successful_result(self):
        """Create successful result."""
        result = PluginOperationResult(
            success=True,
            message="Plugin installed successfully",
            plugin_id="my-plugin@marketplace",
            plugin_name="my-plugin",
            scope="user"
        )
        assert result.success is True
        assert result.plugin_id == "my-plugin@marketplace"

    def test_failed_result(self):
        """Create failed result."""
        result = PluginOperationResult(
            success=False,
            message="Plugin not found"
        )
        assert result.success is False
        assert result.plugin_id is None


class TestPluginUpdateResult:
    """Test plugin update result dataclass."""

    def test_successful_update(self):
        """Create successful update result."""
        result = PluginUpdateResult(
            success=True,
            message="Plugin updated",
            plugin_id="my-plugin@marketplace",
            new_version="2.0.0",
            old_version="1.0.0",
            scope="user"
        )
        assert result.success is True
        assert result.new_version == "2.0.0"
        assert result.already_up_to_date is False

    def test_already_up_to_date(self):
        """Create already up-to-date result."""
        result = PluginUpdateResult(
            success=True,
            message="Plugin already up to date",
            plugin_id="my-plugin@marketplace",
            new_version="1.0.0",
            old_version="1.0.0",
            already_up_to_date=True,
            scope="user"
        )
        assert result.already_up_to_date is True