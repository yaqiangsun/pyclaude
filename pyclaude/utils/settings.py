"""Settings management - handles .claude/settings.json and config.json."""
import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


def get_claude_settings_path() -> str:
    """Get the path to .claude/settings.json."""
    cwd = os.getcwd()
    return os.path.join(cwd, ".claude", "settings.json")


def get_claude_config_path() -> str:
    """Get the path to .claude.json in project root."""
    cwd = os.getcwd()
    return os.path.join(cwd, ".claude.json")


def get_global_settings_path() -> str:
    """Get the global settings path."""
    config_home = os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))
    return os.path.join(config_home, "settings.json")


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file, return None if not found or invalid."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return None


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save JSON file. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


class Settings:
    """Settings manager for Claude Code."""

    def __init__(self):
        self._project_settings: Optional[Dict[str, Any]] = None
        self._claude_json: Optional[Dict[str, Any]] = None
        self._global_settings: Optional[Dict[str, Any]] = None

    def load_project_settings(self) -> Dict[str, Any]:
        """Load .claude/settings.json."""
        if self._project_settings is None:
            path = get_claude_settings_path()
            self._project_settings = load_json_file(path) or {}
        return self._project_settings

    def save_project_settings(self, data: Dict[str, Any]) -> bool:
        """Save .claude/settings.json."""
        path = get_claude_settings_path()
        self._project_settings = data
        return save_json_file(path, data)

    def load_claude_json(self) -> Dict[str, Any]:
        """Load .claude.json from project root."""
        if self._claude_json is None:
            path = get_claude_config_path()
            self._claude_json = load_json_file(path) or {}
        return self._claude_json

    def save_claude_json(self, data: Dict[str, Any]) -> bool:
        """Save .claude.json to project root."""
        path = get_claude_config_path()
        self._claude_json = data
        return save_json_file(path, data)

    def load_global_settings(self) -> Dict[str, Any]:
        """Load global settings.json."""
        if self._global_settings is None:
            path = get_global_settings_path()
            self._global_settings = load_json_file(path) or {}
        return self._global_settings

    def save_global_settings(self, data: Dict[str, Any]) -> bool:
        """Save global settings.json."""
        path = get_global_settings_path()
        self._global_settings = data
        return save_json_file(path, data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value (checks project, then global)."""
        # First check project settings
        project = self.load_project_settings()
        if key in project:
            return project[key]

        # Then check .claude.json
        claude_json = self.load_claude_json()
        if key in claude_json:
            return claude_json[key]

        # Finally check global settings
        global_settings = self.load_global_settings()
        return global_settings.get(key, default)

    def set(self, key: str, value: Any, scope: str = "project") -> bool:
        """Set a setting value."""
        if scope == "project":
            settings = self.load_project_settings()
            settings[key] = value
            return self.save_project_settings(settings)
        elif scope == "claude_json":
            settings = self.load_claude_json()
            settings[key] = value
            return self.save_claude_json(settings)
        elif scope == "global":
            settings = self.load_global_settings()
            settings[key] = value
            return self.save_global_settings(settings)
        return False

    def get_all(self) -> Dict[str, Any]:
        """Get all settings merged (project > claude.json > global)."""
        result = dict(self.load_global_settings())
        result.update(self.load_claude_json())
        result.update(self.load_project_settings())
        return result


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience functions
def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value."""
    return get_settings().get(key, default)


def set_setting(key: str, value: Any, scope: str = "project") -> bool:
    """Set a setting value."""
    return get_settings().set(key, value, scope)


__all__ = [
    "Settings",
    "get_settings",
    "get_setting",
    "set_setting",
    "get_claude_settings_path",
    "get_claude_config_path",
    "get_global_settings_path",
    "load_json_file",
    "save_json_file",
]