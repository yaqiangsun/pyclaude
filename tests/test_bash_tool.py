"""Tests for BashTool."""
import pytest
import asyncio

from pyclaude.tools.bash_tool import (
    BashTool,
    execute_bash,
    parse_command,
    DEFAULT_TIMEOUT_MS,
    BASH_LIST_COMMANDS,
    BASH_SEARCH_COMMANDS,
    BASH_READ_COMMANDS,
)


class TestBashTool:
    """Test BashTool class."""

    def test_tool_name(self):
        """Has correct tool name."""
        tool = BashTool()
        assert tool.name == "Bash"

    def test_input_schema(self):
        """Has correct input schema."""
        tool = BashTool()
        assert tool.input_schema["type"] == "object"
        assert "command" in tool.input_schema["required"]
        assert "command" in tool.input_schema["properties"]


class TestParseCommand:
    """Test parse_command function."""

    def test_parse_ls_command(self):
        """Identifies ls command."""
        result = parse_command("ls -la")
        assert result["is_list"] is True
        assert result["is_search"] is False

    def test_parse_tree_command(self):
        """Identifies tree command."""
        result = parse_command("tree -L 2")
        assert result["is_list"] is True

    def test_parse_grep_command(self):
        """Identifies grep command."""
        result = parse_command("grep -r 'pattern' .")
        assert result["is_search"] is True
        assert result["is_read"] is False

    def test_parse_cat_command(self):
        """Identifies cat command."""
        result = parse_command("cat file.txt")
        assert result["is_read"] is True

    def test_parse_find_command(self):
        """Identifies find command."""
        result = parse_command("find . -name '*.py'")
        assert result["is_search"] is True

    def test_parse_background_command(self):
        """Identifies background command."""
        result = parse_command("npm start &")
        assert result["is_background"] is True

    def test_parse_regular_command(self):
        """Regular command has no flags."""
        result = parse_command("echo hello")
        assert result["is_list"] is False
        assert result["is_search"] is False
        assert result["is_read"] is False
        assert result["is_background"] is False


class TestExecuteBash:
    """Test execute_bash function."""

    @pytest.mark.asyncio
    async def test_execute_echo(self):
        """Can execute echo command."""
        result = await execute_bash(
            {"command": "echo hello"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert "hello" in result["stdout"]
        assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_ls(self):
        """Can execute ls command."""
        result = await execute_bash(
            {"command": "ls"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["exit_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_ls_with_path(self):
        """Can list specific directory."""
        result = await execute_bash(
            {"command": "ls /tmp"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_execute_pwd(self):
        """Can execute pwd command."""
        result = await execute_bash(
            {"command": "pwd"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["stdout"].strip() != ""

    @pytest.mark.asyncio
    async def test_execute_invalid_command(self):
        """Handles invalid command gracefully."""
        result = await execute_bash(
            {"command": "nonexistent_command_xyz"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert result["exit_code"] != 0

    @pytest.mark.asyncio
    async def test_execute_missing_command(self):
        """Fails without command."""
        result = await execute_bash(
            {},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Can specify timeout."""
        result = await execute_bash(
            {"command": "echo test", "timeout": 5000},
            lambda: {},
            lambda x: None,
        )

        assert "duration_ms" in result

    @pytest.mark.asyncio
    async def test_execute_cd_command(self):
        """CD command returns no output on success."""
        result = await execute_bash(
            {"command": "cd /tmp"},
            lambda: {},
            lambda x: None,
        )

        assert result["has_no_output"] is True


class TestBashConstants:
    """Test bash tool constants."""

    def test_list_commands(self):
        """BASH_LIST_COMMANDS contains expected commands."""
        assert "ls" in BASH_LIST_COMMANDS
        assert "tree" in BASH_LIST_COMMANDS
        assert "du" in BASH_LIST_COMMANDS

    def test_search_commands(self):
        """BASH_SEARCH_COMMANDS contains expected commands."""
        assert "grep" in BASH_SEARCH_COMMANDS
        assert "find" in BASH_SEARCH_COMMANDS
        assert "rg" in BASH_SEARCH_COMMANDS

    def test_read_commands(self):
        """BASH_READ_COMMANDS contains expected commands."""
        assert "cat" in BASH_READ_COMMANDS
        assert "head" in BASH_READ_COMMANDS
        assert "tail" in BASH_READ_COMMANDS

    def test_default_timeout(self):
        """Default timeout is 30 minutes."""
        assert DEFAULT_TIMEOUT_MS == 30 * 60 * 1000