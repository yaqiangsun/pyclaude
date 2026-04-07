"""Tests for memory scan utilities."""
import json
import os
import tempfile
from pathlib import Path
import pytest

from pyclaude.memdir.memory_scan import (
    MemoryHeader,
    MEMORY_TYPES,
    MAX_MEMORY_FILES,
    parse_memory_type,
    scan_memory_files,
    format_memory_manifest,
    scan_memories,
    find_relevant_memories,
)


class TestParseMemoryType:
    """Test memory type parsing."""

    def test_valid_memory_types(self):
        """Test valid memory types are recognized."""
        assert parse_memory_type('user') == 'user'
        assert parse_memory_type('feedback') == 'feedback'
        assert parse_memory_type('project') == 'project'
        assert parse_memory_type('reference') == 'reference'

    def test_invalid_memory_type(self):
        """Test invalid memory types return None."""
        assert parse_memory_type('invalid') is None
        assert parse_memory_type('') is None
        assert parse_memory_type(123) is None
        assert parse_memory_type(None) is None

    def test_memory_types_constant(self):
        """Test MEMORY_TYPES contains expected types."""
        assert 'user' in MEMORY_TYPES
        assert 'feedback' in MEMORY_TYPES
        assert 'project' in MEMORY_TYPES
        assert 'reference' in MEMORY_TYPES


class TestMemoryHeader:
    """Test MemoryHeader dataclass."""

    def test_memory_header_creation(self):
        """Test creating a MemoryHeader."""
        header = MemoryHeader(
            filename='test.md',
            file_path='/path/to/test.md',
            mtime_ms=1234567890.0,
            description='Test description',
            type='user',
        )
        assert header.filename == 'test.md'
        assert 'Test' in header.description
        assert header.type == 'user'

    def test_memory_header_optional_fields(self):
        """Test optional fields can be None."""
        header = MemoryHeader(
            filename='test.md',
            file_path='/path/to/test.md',
            mtime_ms=1234567890.0,
            description=None,
            type=None,
        )
        assert header.description is None
        assert header.type is None


class TestScanMemoryFiles:
    """Test scanning memory files."""

    def test_scan_empty_directory(self):
        """Scan empty directory returns empty list."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            result = asyncio.run(scan_memory_files(tmpdir))
            assert result == []

    def test_scan_nonexistent_directory(self):
        """Scan nonexistent directory returns empty list."""
        import asyncio
        result = asyncio.run(scan_memory_files('/nonexistent/path'))
        assert result == []

    def test_scan_with_memory_files(self):
        """Scan directory with .md files."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some memory files
            (Path(tmpdir) / 'memory1.md').write_text(
                '---\ndescription: First memory\ntype: user\n---\n\nFirst content'
            )
            (Path(tmpdir) / 'memory2.md').write_text(
                '---\ndescription: Second memory\ntype: project\n---\n\nSecond content'
            )

            result = asyncio.run(scan_memory_files(tmpdir))
            assert len(result) == 2

            # Check files are sorted by mtime (newest first)
            # Since we just created them, order may vary
            filenames = [r.filename for r in result]
            assert 'memory1.md' in filenames
            assert 'memory2.md' in filenames

    def test_scan_excludes_memory_md(self):
        """Scan excludes MEMORY.md file."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'MEMORY.md').write_text('# Memory index')
            (Path(tmpdir) / 'test.md').write_text('Test')

            result = asyncio.run(scan_memory_files(tmpdir))
            filenames = [r.filename for r in result]
            assert 'MEMORY.md' not in filenames
            assert 'test.md' in filenames

    def test_scan_respects_max_files(self):
        """Scan respects MAX_MEMORY_FILES limit."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create more than MAX_MEMORY_FILES
            for i in range(MAX_MEMORY_FILES + 10):
                (Path(tmpdir) / f'memory{i}.md').write_text('Test')

            result = asyncio.run(scan_memory_files(tmpdir))
            assert len(result) <= MAX_MEMORY_FILES

    def test_scan_extracts_type_from_frontmatter(self):
        """Scan extracts type from frontmatter."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'test.md').write_text(
                '---\ndescription: Test\ntype: feedback\n---\n\nContent'
            )

            result = asyncio.run(scan_memory_files(tmpdir))
            assert len(result) == 1
            assert result[0].type == 'feedback'

    def test_scan_extracts_description(self):
        """Scan extracts description from frontmatter."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'test.md').write_text(
                '---\ndescription: My test memory\n---\n\nContent'
            )

            result = asyncio.run(scan_memory_files(tmpdir))
            assert len(result) == 1
            assert result[0].description == 'My test memory'


class TestFormatMemoryManifest:
    """Test formatting memory manifest."""

    def test_format_empty_manifest(self):
        """Format empty list."""
        result = format_memory_manifest([])
        assert result == ''

    def test_format_basic_manifest(self):
        """Format basic manifest."""
        headers = [
            MemoryHeader('test.md', '/path/test.md', 1234567890.0, 'Test desc', 'user'),
        ]
        result = format_memory_manifest(headers)
        assert 'test.md' in result
        assert 'Test desc' in result
        assert '[user]' in result

    def test_format_manifest_without_type(self):
        """Format manifest without type."""
        headers = [
            MemoryHeader('test.md', '/path/test.md', 1234567890.0, 'Test desc', None),
        ]
        result = format_memory_manifest(headers)
        assert 'test.md' in result
        assert '[user]' not in result


class TestScanMemories:
    """Test legacy scan_memories function."""

    def test_scan_memories_returns_dicts(self):
        """scan_memories returns list of dicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'test.md').write_text('Test')

            result = scan_memories(tmpdir)
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], dict)
                assert 'filename' in result[0]


class TestFindRelevantMemories:
    """Test finding relevant memories."""

    def test_find_relevant_with_empty_query(self):
        """Find with empty query returns recent memories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'test1.md').write_text('Content 1')
            (Path(tmpdir) / 'test2.md').write_text('Content 2')

            result = find_relevant_memories(tmpdir, '')
            assert len(result) <= 10

    def test_find_relevant_matches_description(self):
        """Find matches description content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'test1.md').write_text(
                '---\ndescription: Python programming\n---\n\nContent'
            )
            (Path(tmpdir) / 'test2.md').write_text(
                '---\ndescription: JavaScript coding\n---\n\nContent'
            )

            result = find_relevant_memories(tmpdir, 'python')
            # Should match 'python' in description
            assert len(result) > 0
            # The one with 'Python' should have higher score
            if len(result) > 1:
                assert result[0]['score'] >= result[1]['score']

    def test_find_relevant_matches_filename(self):
        """Find matches filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'python-tips.md').write_text('Content')
            (Path(tmpdir) / 'other.md').write_text('Content')

            result = find_relevant_memories(tmpdir, 'python')
            assert len(result) > 0
            assert 'python-tips.md' in result[0]['filename']


class TestScanMemoryFilesAsync:
    """Test async scan_memory_files function."""

    def test_scan_with_signal_param(self):
        """Test that signal param is accepted (even if ignored)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise even with signal
            import asyncio
            result = asyncio.run(scan_memory_files(tmpdir, signal=None))
            assert result == []