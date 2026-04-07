"""Tests for plugin schemas and validation."""
import pytest
from pyclaude.services.plugins.schemas import (
    validate_plugin_name,
    validate_marketplace_name,
    is_blocked_official_name,
    is_marketplace_auto_update,
    ALLOWED_OFFICIAL_MARKETPLACE_NAMES,
)


class TestValidatePluginName:
    """Test plugin name validation."""

    def test_valid_plugin_name(self):
        """Valid plugin names pass validation."""
        valid, error = validate_plugin_name("my-plugin")
        assert valid is True
        assert error is None

        valid, error = validate_plugin_name("awesome-plugin")
        assert valid is True

    def test_empty_plugin_name(self):
        """Empty plugin name fails validation."""
        valid, error = validate_plugin_name("")
        assert valid is False
        assert "cannot be empty" in error

    def test_plugin_name_with_spaces(self):
        """Plugin names with spaces fail validation."""
        valid, error = validate_plugin_name("my plugin")
        assert valid is False
        assert "cannot contain spaces" in error


class TestValidateMarketplaceName:
    """Test marketplace name validation."""

    def test_valid_marketplace_name(self):
        """Valid marketplace names pass validation."""
        valid, error = validate_marketplace_name("my-marketplace")
        assert valid is True
        assert error is None

        valid, error = validate_marketplace_name("awesome-plugins")
        assert valid is True

    def test_empty_marketplace_name(self):
        """Empty marketplace name fails validation."""
        valid, error = validate_marketplace_name("")
        assert valid is False

    def test_marketplace_name_with_spaces(self):
        """Marketplace names with spaces fail validation."""
        valid, error = validate_marketplace_name("my marketplace")
        assert valid is False
        assert "cannot contain spaces" in error

    def test_marketplace_name_with_path_separator(self):
        """Marketplace names with path separators fail."""
        valid, error = validate_marketplace_name("my/marketplace")
        assert valid is False
        assert "cannot contain path separators" in error

    def test_marketplace_name_inline_reserved(self):
        """Inline is a reserved marketplace name."""
        valid, error = validate_marketplace_name("inline")
        assert valid is False
        assert "reserved" in error.lower()

    def test_marketplace_name_builtin_reserved(self):
        """Builtin is a reserved marketplace name."""
        valid, error = validate_marketplace_name("builtin")
        assert valid is False
        assert "reserved" in error.lower()


class TestIsBlockedOfficialName:
    """Test official marketplace name blocking."""

    def test_allowed_official_names(self):
        """Allowed official names are not blocked."""
        for name in ALLOWED_OFFICIAL_MARKETPLACE_NAMES:
            assert is_blocked_official_name(name) is False

    def test_impersonating_names_blocked(self):
        """Names impersonating official marketplaces are blocked."""
        # These are in ALLOWED_OFFICIAL_MARKETPLACE_NAMES, so they're allowed
        assert is_blocked_official_name("anthropic-marketplace") is False
        # Non-ASCII characters are blocked
        assert is_blocked_official_name("anthropic-markętplace") is True


class TestIsMarketplaceAutoUpdate:
    """Test marketplace auto-update logic."""

    def test_official_marketplace_auto_update(self):
        """Official marketplaces have auto-update enabled."""
        assert is_marketplace_auto_update("claude-code-marketplace") is True
        assert is_marketplace_auto_update("anthropic-marketplace") is True

    def test_knowledge_work_no_auto_update(self):
        """knowledge-work-plugins has auto-update disabled."""
        assert is_marketplace_auto_update("knowledge-work-plugins") is False

    def test_custom_marketplace_no_auto_update(self):
        """Custom marketplaces don't have auto-update."""
        assert is_marketplace_auto_update("my-custom-marketplace") is False

    def test_entry_overrides_default(self):
        """Entry can override auto-update setting."""
        # Entry with autoUpdate: true
        assert is_marketplace_auto_update("knowledge-work-plugins", {"autoUpdate": True}) is True
        # Entry with autoUpdate: false
        assert is_marketplace_auto_update("claude-code-marketplace", {"autoUpdate": False}) is False