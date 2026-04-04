"""Tests for tool module."""
import pytest
from pyclaude.tool import (
    ToolType,
    ToolStatus,
    ToolInputSchema,
    ToolDefinition,
)


class TestToolType:
    """Test ToolType enum."""

    def test_tool_types_exist(self):
        """All expected tool types exist."""
        assert ToolType.BASH == 'bash'
        assert ToolType.EDIT == 'edit'
        assert ToolType.READ == 'read'
        assert ToolType.AGENT == 'agent'
        assert ToolType.TOOL == 'tool'
        assert ToolType.MCP == 'mcp'
        assert ToolType.WEBSEARCH == 'websearch'
        assert ToolType.REPL == 'repl'
        assert ToolType.SKILL == 'skill'
        assert ToolType.COMPACT == 'compact'
        assert ToolType.EXIT == 'exit'


class TestToolStatus:
    """Test ToolStatus enum."""

    def test_tool_statuses_exist(self):
        """All expected tool statuses exist."""
        assert ToolStatus.PENDING == 'pending'
        assert ToolStatus.RUNNING == 'running'
        assert ToolStatus.COMPLETED == 'completed'
        assert ToolStatus.ERROR == 'error'
        assert ToolStatus.DENIED == 'denied'


class TestToolInputSchema:
    """Test ToolInputSchema."""

    def test_default_values(self):
        """Default schema has empty properties and required."""
        schema = ToolInputSchema()
        assert schema.type == 'object'
        assert schema.properties == {}
        assert schema.required == []

    def test_with_properties(self):
        """Schema can have properties."""
        schema = ToolInputSchema(
            properties={"name": {"type": "string"}},
            required=["name"]
        )
        assert "name" in schema.properties
        assert "name" in schema.required


class TestToolDefinition:
    """Test ToolDefinition."""

    def test_tool_definition_creation(self):
        """ToolDefinition can be created."""
        schema = ToolInputSchema(
            properties={"path": {"type": "string"}},
            required=["path"]
        )
        tool_def = ToolDefinition(
            name="Read",
            description="Read a file",
            input_schema=schema,
        )
        assert tool_def.name == "Read"
        assert tool_def.description == "Read a file"