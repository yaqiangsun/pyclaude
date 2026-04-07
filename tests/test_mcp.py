"""Tests for MCP command."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pyclaude.commands.mcp.mcp import (
    parse_mcp_args,
    load_server_config,
    save_server_config,
    get_pid_file,
    save_pid,
    load_pid,
    is_process_running,
)


class TestParseMcpArgs:
    """Test MCP argument parsing."""

    def test_empty_args_returns_list(self):
        """Empty args returns list type."""
        result = parse_mcp_args("")
        assert result['type'] == 'list'

    def test_list_command(self):
        """Parse list command."""
        result = parse_mcp_args("list")
        assert result['type'] == 'list'

    def test_add_command(self):
        """Parse add command."""
        result = parse_mcp_args("add myserver npx -y some-package")
        assert result['type'] == 'add'
        assert result['name'] == 'myserver'
        assert result['command'] == 'npx -y some-package'

    def test_add_no_args(self):
        """Parse add with no args."""
        result = parse_mcp_args("add")
        assert result['type'] == 'add'
        assert result.get('name') is None

    def test_remove_command(self):
        """Parse remove command."""
        result = parse_mcp_args("remove myserver")
        assert result['type'] == 'remove'
        assert result['name'] == 'myserver'

    def test_remove_alias(self):
        """Parse delete alias."""
        result = parse_mcp_args("delete myserver")
        assert result['type'] == 'remove'
        assert result['name'] == 'myserver'

    def test_start_command(self):
        """Parse start command."""
        result = parse_mcp_args("start myserver")
        assert result['type'] == 'start'
        assert result['name'] == 'myserver'

    def test_stop_command(self):
        """Parse stop command."""
        result = parse_mcp_args("stop myserver")
        assert result['type'] == 'stop'
        assert result['name'] == 'myserver'

    def test_get_command(self):
        """Parse get command."""
        result = parse_mcp_args("get myserver")
        assert result['type'] == 'get'
        assert result['name'] == 'myserver'

    def test_unknown_command(self):
        """Unknown command."""
        result = parse_mcp_args("unknown")
        assert result['type'] == 'unknown'


class TestMcpServerConfig:
    """Test MCP server configuration."""

    @patch('pyclaude.commands.mcp.mcp.MCP_DIR')
    def test_load_server_config_not_found(self, mock_mcp_dir):
        """Load config returns None when not found."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_mcp_dir.__truediv__ = MagicMock(return_value=mock_path)
        result = load_server_config('myserver')
        assert result is None

    @patch('pyclaude.commands.mcp.mcp.MCP_DIR')
    def test_load_server_config_success(self, mock_mcp_dir):
        """Load config returns config."""
        mock_file = MagicMock()
        mock_file.stem = 'myserver'
        mock_file.exists.return_value = True
        mock_mcp_dir.__truediv__ = MagicMock(return_value=mock_file)

        with patch('pyclaude.commands.mcp.mcp.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                'command': 'npx',
                'args': ['-y', 'some-package'],
                'enabled': True
            })
            result = load_server_config('myserver')
            assert result is not None
            assert result['command'] == 'npx'
            assert result['args'] == ['-y', 'some-package']

    @patch('pyclaude.commands.mcp.mcp.ensure_dirs')
    @patch('pyclaude.commands.mcp.mcp.MCP_DIR')
    def test_save_server_config(self, mock_mcp_dir, mock_ensure_dirs):
        """Save server config."""
        mock_file = MagicMock()
        mock_mcp_dir.__truediv__ = MagicMock(return_value=mock_file)

        with patch('builtins.open', MagicMock()) as mock_open:
            save_server_config('myserver', {'command': 'npx', 'args': []})
            mock_open.assert_called_once()
            # Check json.dump was called
            call_args = mock_open.return_value.__enter__.return_value.write.call_args
            assert call_args is not None


class TestMcpPidManagement:
    """Test MCP PID management."""

    @patch('pyclaude.commands.mcp.mcp.MCP_PID_DIR')
    def test_get_pid_file(self, mock_pid_dir):
        """Get PID file path."""
        mock_pid_dir.__truediv__ = MagicMock(return_value=Path('/test/myserver.pid'))
        result = get_pid_file('myserver')
        assert result.name == 'myserver.pid'

    @patch('pyclaude.commands.mcp.mcp.MCP_PID_DIR')
    def test_save_pid(self, mock_pid_dir):
        """Save PID."""
        mock_file = MagicMock()
        mock_pid_dir.__truediv__ = MagicMock(return_value=mock_file)

        with patch('pyclaude.commands.mcp.mcp.open', MagicMock()) as mock_open:
            save_pid('myserver', 12345)
            mock_open.return_value.__enter__.return_value.write.assert_called_once_with('12345')

    @patch('pyclaude.commands.mcp.mcp.MCP_PID_DIR')
    def test_load_pid(self, mock_pid_dir):
        """Load PID."""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_pid_dir.__truediv__ = MagicMock(return_value=mock_file)

        with patch('pyclaude.commands.mcp.mcp.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '12345'
            result = load_pid('myserver')
            assert result == 12345


class TestIsProcessRunning:
    """Test process running check."""

    @patch('os.kill')
    def test_process_running(self, mock_kill):
        """Process is running."""
        mock_kill.return_value = None
        result = is_process_running(12345)
        assert result is True
        mock_kill.assert_called_once_with(12345, 0)

    @patch('os.kill')
    def test_process_not_running(self, mock_kill):
        """Process is not running."""
        mock_kill.side_effect = OSError("No such process")
        result = is_process_running(99999)
        assert result is False


class TestMcpArgsEdgeCases:
    """Test edge cases in MCP argument parsing."""

    def test_add_with_empty_command(self):
        """Add with no command."""
        result = parse_mcp_args("add myserver")
        assert result['type'] == 'add'
        assert result['name'] == 'myserver'
        assert result['command'] == ''

    def test_start_no_name(self):
        """Start with no name."""
        result = parse_mcp_args("start")
        assert result['type'] == 'start'
        assert result.get('name') is None

    def test_stop_no_name(self):
        """Stop with no name."""
        result = parse_mcp_args("stop")
        assert result['type'] == 'stop'
        assert result.get('name') is None

    def test_remove_no_name(self):
        """Remove with no name."""
        result = parse_mcp_args("remove")
        assert result['type'] == 'remove'
        assert result.get('name') is None

    def test_get_no_name(self):
        """Get with no name."""
        result = parse_mcp_args("get")
        assert result['type'] == 'get'
        assert result.get('name') is None

    def test_list_with_flag(self):
        """List with flag."""
        result = parse_mcp_args("list --verbose")
        assert result['type'] == 'list'