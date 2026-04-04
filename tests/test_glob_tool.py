"""Tests for GlobTool."""
import pytest
import os
import tempfile
import asyncio
from pathlib import Path

from pyclaude.tools.glob_tool import (
    glob_pattern,
    execute_glob,
    GlobToolInput,
    MAX_RESULTS,
)


class TestGlobPattern:
    """Test glob_pattern function."""

    def test_glob_all_py_files(self, tmp_path):
        """Can find all Python files."""
        # Create test files
        (tmp_path / "test1.py").touch()
        (tmp_path / "test2.py").touch()
        (tmp_path / "readme.txt").touch()

        results = glob_pattern("*.py", str(tmp_path))

        assert len(results) == 2
        assert any("test1.py" in r for r in results)
        assert any("test2.py" in r for r in results)

    def test_glob_nested_files(self, tmp_path):
        """Can find files in nested directories."""
        # Create nested structure - glob walks all subdirs
        (tmp_path / "file.py").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.py").touch()

        # The glob_pattern uses os.walk and fnmatch
        results = glob_pattern("*.py", str(tmp_path))

        # Finds both files since os.walk recurses
        assert len(results) == 2
        assert any("file.py" in r for r in results)
        assert any("nested.py" in r for r in results)

    def test_glob_no_matches(self, tmp_path):
        """Returns empty list when no matches."""
        (tmp_path / "readme.txt").touch()

        results = glob_pattern("*.py", str(tmp_path))

        assert results == []

    def test_glob_with_specific_path(self, tmp_path):
        """Can search in specific subdirectory."""
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "main.py").touch()
        (tmp_path / "other.py").touch()

        results = glob_pattern("*.py", str(subdir))

        assert len(results) == 1
        assert "main.py" in results[0]


class TestExecuteGlob:
    """Test execute_glob function."""

    @pytest.mark.asyncio
    async def test_execute_glob_success(self, tmp_path):
        """Execute glob returns success result."""
        (tmp_path / "test.py").touch()

        # Must specify path since execute_glob uses get_cwd() by default
        result = await execute_glob(
            {"pattern": "*.py", "path": str(tmp_path)},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["numFiles"] == 1
        assert len(result["filenames"]) == 1
        assert "durationMs" in result

    @pytest.mark.asyncio
    async def test_execute_glob_missing_pattern(self):
        """Execute glob fails without pattern."""
        result = await execute_glob(
            {},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_glob_truncates_results(self, tmp_path):
        """Results are truncated when exceeding MAX_RESULTS."""
        # Create more files than MAX_RESULTS
        for i in range(MAX_RESULTS + 10):
            (tmp_path / f"file{i}.py").touch()

        result = await execute_glob(
            {"pattern": "*.py"},
            lambda: {},
            lambda x: None,
        )

        assert result["truncated"] is True
        assert result["numFiles"] == MAX_RESULTS
        assert len(result["filenames"]) == MAX_RESULTS

    @pytest.mark.asyncio
    async def test_execute_glob_with_path(self, tmp_path):
        """Can search in specified path."""
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "main.py").touch()

        result = await execute_glob(
            {"pattern": "*.py", "path": str(subdir)},
            lambda: {},
            lambda x: None,
        )

        assert result["success"] is True
        assert result["numFiles"] == 1


class TestGlobToolInput:
    """Test GlobToolInput dataclass."""

    def test_default_values(self):
        """Has correct defaults."""
        inp = GlobToolInput(pattern="*.py")
        assert inp.pattern == "*.py"
        assert inp.path is None

    def test_with_path(self):
        """Can specify path."""
        inp = GlobToolInput(pattern="*.py", path="/tmp")
        assert inp.path == "/tmp"