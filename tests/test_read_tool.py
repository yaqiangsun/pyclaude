"""Tests for ReadTool."""
import pytest
import os
import tempfile

from pyclaude.tools.read_tool import (
    execute_read,
    ReadToolInput,
    ReadToolOutput,
    MAX_CHARS,
)


class TestExecuteRead:
    """Test execute_read function."""

    @pytest.mark.asyncio
    async def test_read_file(self, tmp_path):
        """Can read a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        result = await execute_read(
            {"file_path": str(test_file)},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["content"] == "Hello, World!"
        assert result["lines"] == 1
        assert result["truncated"] is False

    @pytest.mark.asyncio
    async def test_read_multiline_file(self, tmp_path):
        """Can read multiline file."""
        test_file = tmp_path / "lines.txt"
        test_file.write_text("line1\nline2\nline3")

        result = await execute_read(
            {"file_path": str(test_file)},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["lines"] == 3

    @pytest.mark.asyncio
    async def test_read_with_offset(self, tmp_path):
        """Can read with offset."""
        test_file = tmp_path / "lines.txt"
        test_file.write_text("line1\nline2\nline3")

        result = await execute_read(
            {"file_path": str(test_file), "offset": 1},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert "line2" in result["content"]
        assert "line1" not in result["content"]

    @pytest.mark.asyncio
    async def test_read_with_limit(self, tmp_path):
        """Can read with limit."""
        test_file = tmp_path / "lines.txt"
        test_file.write_text("line1\nline2\nline3")

        result = await execute_read(
            {"file_path": str(test_file), "limit": 2},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["lines"] == 2

    @pytest.mark.asyncio
    async def test_read_with_offset_and_limit(self, tmp_path):
        """Can read with both offset and limit."""
        test_file = tmp_path / "lines.txt"
        test_file.write_text("line1\nline2\nline3\nline4")

        result = await execute_read(
            {"file_path": str(test_file), "offset": 1, "limit": 2},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert "line2" in result["content"]
        assert "line4" not in result["content"]

    @pytest.mark.asyncio
    async def test_read_missing_file(self):
        """Fails when file doesn't exist."""
        result = await execute_read(
            {"file_path": "/nonexistent/file.txt"},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_read_missing_file_path(self):
        """Fails when file_path is empty."""
        result = await execute_read(
            {},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_read_directory_fails(self, tmp_path):
        """Fails when path is a directory."""
        test_dir = tmp_path / "subdir"
        test_dir.mkdir()

        result = await execute_read(
            {"file_path": str(test_dir)},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert "not a file" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_read_truncates_large_file(self, tmp_path):
        """Truncates very large files."""
        # Create file larger than MAX_CHARS
        test_file = tmp_path / "large.txt"
        large_content = "x" * (MAX_CHARS + 1000)
        test_file.write_text(large_content)

        result = await execute_read(
            {"file_path": str(test_file)},
            lambda: {},
            lambda x: None,
        )

        assert result["truncated"] is True
        assert len(result["content"]) <= MAX_CHARS


class TestReadToolInput:
    """Test ReadToolInput dataclass."""

    def test_default_values(self):
        """Has correct defaults."""
        inp = ReadToolInput(file_path="test.txt")
        assert inp.file_path == "test.txt"
        assert inp.offset is None
        assert inp.limit is None

    def test_with_offset_and_limit(self):
        """Can specify offset and limit."""
        inp = ReadToolInput(file_path="test.txt", offset=10, limit=5)
        assert inp.offset == 10
        assert inp.limit == 5


class TestReadToolOutput:
    """Test ReadToolOutput dataclass."""

    def test_creation(self):
        """Can create output."""
        out = ReadToolOutput(content="test", lines=1, truncated=False)
        assert out.content == "test"
        assert out.lines == 1
        assert out.truncated is False