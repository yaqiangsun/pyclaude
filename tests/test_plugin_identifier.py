"""Tests for plugin identifier parsing."""
import pytest
from pyclaude.services.plugins.plugin_identifier import (
    parse_plugin_identifier,
    build_plugin_id,
    is_official_marketplace_name,
    scope_to_setting_source,
    setting_source_to_scope,
)


class TestParsePluginIdentifier:
    """Test plugin identifier parsing."""

    def test_parse_simple_plugin_name(self):
        """Parse plugin name without marketplace."""
        result = parse_plugin_identifier("my-plugin")
        assert result.name == "my-plugin"
        assert result.marketplace is None

    def test_parse_plugin_with_marketplace(self):
        """Parse plugin@marketplace format."""
        result = parse_plugin_identifier("my-plugin@claude-plugins-official")
        assert result.name == "my-plugin"
        assert result.marketplace == "claude-plugins-official"

    def test_parse_plugin_with_at_sign_in_version(self):
        """Handle plugin@version@marketplace format (if applicable)."""
        # Currently just parses first @
        result = parse_plugin_identifier("plugin@v1.0.0@marketplace")
        assert result.name == "plugin"
        assert result.marketplace == "v1.0.0@marketplace"

    def test_parse_empty_string(self):
        """Parse empty string."""
        result = parse_plugin_identifier("")
        assert result.name == ""
        assert result.marketplace is None


class TestBuildPluginId:
    """Test plugin ID building."""

    def test_build_without_marketplace(self):
        """Build plugin ID without marketplace."""
        result = build_plugin_id("my-plugin", None)
        assert result == "my-plugin"

    def test_build_with_marketplace(self):
        """Build plugin ID with marketplace."""
        result = build_plugin_id("my-plugin", "claude-plugins-official")
        assert result == "my-plugin@claude-plugins-official"


class TestIsOfficialMarketplaceName:
    """Test official marketplace name detection."""

    def test_official_marketplace_names(self):
        """Recognize official marketplace names."""
        assert is_official_marketplace_name("claude-code-marketplace") is True
        assert is_official_marketplace_name("claude-code-plugins") is True
        assert is_official_marketplace_name("anthropic-marketplace") is True

    def test_custom_marketplace_names(self):
        """Custom marketplaces are not official."""
        assert is_official_marketplace_name("my-marketplace") is False
        assert is_official_marketplace_name("third-party-plugins") is False


class TestScopeConversion:
    """Test scope and setting source conversion."""

    def test_scope_to_setting_source(self):
        """Convert scope to setting source."""
        assert scope_to_setting_source("user") == "userSettings"
        assert scope_to_setting_source("project") == "projectSettings"
        assert scope_to_setting_source("local") == "localSettings"

    def test_setting_source_to_scope(self):
        """Convert setting source to scope."""
        assert setting_source_to_scope("userSettings") == "user"
        assert setting_source_to_scope("projectSettings") == "project"
        assert setting_source_to_scope("localSettings") == "local"

    def test_roundtrip_conversion(self):
        """Scope conversion is reversible."""
        for scope, source in [("user", "userSettings"), ("project", "projectSettings"), ("local", "localSettings")]:
            result = scope_to_setting_source(scope)
            assert result == source
            back = setting_source_to_scope(result)
            assert back == scope