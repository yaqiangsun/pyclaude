"""Settings management - handles .claude/settings.json and .claude.json."""
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


def get_user_claude_settings_path() -> str:
    """Get the path to ~/.claude/settings.json (user home directory)."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".claude", "settings.json")


def get_user_claude_config_path() -> str:
    """Get the path to ~/.claude.json (user home directory)."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".claude.json")


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


# Settings keys for model and API configuration
SETTING_MODEL = "model"
SETTING_PREFERRED_MODEL = "preferred_model"
SETTING_BASE_URL = "baseUrl"
SETTING_API_KEY = "apiKey"
SETTING_API_URL = "apiUrl"
SETTING_ENV = "env"


class Settings:
    """Settings manager for Claude Code."""

    def __init__(self):
        self._project_settings: Optional[Dict[str, Any]] = None
        self._claude_json: Optional[Dict[str, Any]] = None
        self._global_settings: Optional[Dict[str, Any]] = None
        self._user_settings: Optional[Dict[str, Any]] = None
        self._user_claude_json: Optional[Dict[str, Any]] = None

    def load_project_settings(self) -> Dict[str, Any]:
        """Load .claude/settings.json from current project."""
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
        """Load global settings.json (~/.config/claude/settings.json)."""
        if self._global_settings is None:
            path = get_global_settings_path()
            self._global_settings = load_json_file(path) or {}
        return self._global_settings

    def save_global_settings(self, data: Dict[str, Any]) -> bool:
        """Save global settings.json."""
        path = get_global_settings_path()
        self._global_settings = data
        return save_json_file(path, data)

    def load_user_settings(self) -> Dict[str, Any]:
        """Load ~/.claude/settings.json (user home directory)."""
        if self._user_settings is None:
            path = get_user_claude_settings_path()
            self._user_settings = load_json_file(path) or {}
        return self._user_settings

    def load_user_claude_json(self) -> Dict[str, Any]:
        """Load ~/.claude.json (user home directory)."""
        if self._user_claude_json is None:
            path = get_user_claude_config_path()
            self._user_claude_json = load_json_file(path) or {}
        return self._user_claude_json

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
        """Get all settings merged (project > user > global)."""
        result = dict(self.load_global_settings())
        result.update(self.load_user_claude_json())
        result.update(self.load_user_settings())
        result.update(self.load_claude_json())
        result.update(self.load_project_settings())
        return result

    def _get_from_env(self, settings: Dict[str, Any], key: str) -> Optional[str]:
        """Get value from env block in settings."""
        if SETTING_ENV in settings and isinstance(settings[SETTING_ENV], dict):
            return settings[SETTING_ENV].get(key)
        return None

    def get_model(self) -> Optional[str]:
        """Get model from settings (checks project, user, global in order)."""
        # Check project .claude/settings.json first
        project = self.load_project_settings()
        if SETTING_MODEL in project:
            return project[SETTING_MODEL]
        if SETTING_PREFERRED_MODEL in project:
            return project[SETTING_PREFERRED_MODEL]
        # Check env block
        env_model = self._get_from_env(project, 'ANTHROPIC_DEFAULT_SONNET_MODEL')
        if not env_model:
            env_model = self._get_from_env(project, 'ANTHROPIC_DEFAULT_OPUS_MODEL')
        if not env_model:
            env_model = self._get_from_env(project, 'ANTHROPIC_MODEL')
        if env_model:
            return env_model

        # Check project .claude.json
        claude_json = self.load_claude_json()
        if SETTING_MODEL in claude_json:
            return claude_json[SETTING_MODEL]
        if SETTING_PREFERRED_MODEL in claude_json:
            return claude_json[SETTING_PREFERRED_MODEL]
        env_model = self._get_from_env(claude_json, 'ANTHROPIC_DEFAULT_SONNET_MODEL')
        if not env_model:
            env_model = self._get_from_env(claude_json, 'ANTHROPIC_DEFAULT_OPUS_MODEL')
        if not env_model:
            env_model = self._get_from_env(claude_json, 'ANTHROPIC_MODEL')
        if env_model:
            return env_model

        # Check user ~/.claude/settings.json
        user_settings = self.load_user_settings()
        if SETTING_MODEL in user_settings:
            return user_settings[SETTING_MODEL]
        if SETTING_PREFERRED_MODEL in user_settings:
            return user_settings[SETTING_PREFERRED_MODEL]
        env_model = self._get_from_env(user_settings, 'ANTHROPIC_DEFAULT_SONNET_MODEL')
        if not env_model:
            env_model = self._get_from_env(user_settings, 'ANTHROPIC_DEFAULT_OPUS_MODEL')
        if not env_model:
            env_model = self._get_from_env(user_settings, 'ANTHROPIC_MODEL')
        if env_model:
            return env_model

        # Check user ~/.claude.json
        user_claude_json = self.load_user_claude_json()
        if SETTING_MODEL in user_claude_json:
            return user_claude_json[SETTING_MODEL]
        if SETTING_PREFERRED_MODEL in user_claude_json:
            return user_claude_json[SETTING_PREFERRED_MODEL]
        env_model = self._get_from_env(user_claude_json, 'ANTHROPIC_DEFAULT_SONNET_MODEL')
        if not env_model:
            env_model = self._get_from_env(user_claude_json, 'ANTHROPIC_DEFAULT_OPUS_MODEL')
        if not env_model:
            env_model = self._get_from_env(user_claude_json, 'ANTHROPIC_MODEL')
        if env_model:
            return env_model

        # Finally check global settings
        global_settings = self.load_global_settings()
        return global_settings.get(SETTING_MODEL) or global_settings.get(SETTING_PREFERRED_MODEL)

    def get_base_url(self) -> Optional[str]:
        """Get base URL from settings (checks project, user, global in order)."""
        # Check project .claude/settings.json first
        project = self.load_project_settings()
        if SETTING_BASE_URL in project:
            return project[SETTING_BASE_URL]
        # Check env block in project settings
        env_url = self._get_from_env(project, 'ANTHROPIC_BASE_URL')
        if env_url:
            return env_url

        # Check project .claude.json
        claude_json = self.load_claude_json()
        if SETTING_BASE_URL in claude_json:
            return claude_json[SETTING_BASE_URL]
        env_url = self._get_from_env(claude_json, 'ANTHROPIC_BASE_URL')
        if env_url:
            return env_url

        # Also check apiUrl alias in project
        if SETTING_API_URL in project:
            return project[SETTING_API_URL]
        if SETTING_API_URL in claude_json:
            return claude_json[SETTING_API_URL]

        # Check user ~/.claude/settings.json
        user_settings = self.load_user_settings()
        if SETTING_BASE_URL in user_settings:
            return user_settings[SETTING_BASE_URL]
        env_url = self._get_from_env(user_settings, 'ANTHROPIC_BASE_URL')
        if env_url:
            return env_url
        if SETTING_API_URL in user_settings:
            return user_settings[SETTING_API_URL]

        # Check user ~/.claude.json
        user_claude_json = self.load_user_claude_json()
        if SETTING_BASE_URL in user_claude_json:
            return user_claude_json[SETTING_BASE_URL]
        env_url = self._get_from_env(user_claude_json, 'ANTHROPIC_BASE_URL')
        if env_url:
            return env_url
            return user_claude_json[SETTING_BASE_URL]
        if SETTING_API_URL in user_claude_json:
            return user_claude_json[SETTING_API_URL]

        # Finally check global settings
        global_settings = self.load_global_settings()
        return global_settings.get(SETTING_BASE_URL) or global_settings.get(SETTING_API_URL)
        if SETTING_API_URL in claude_json:
            return claude_json[SETTING_API_URL]

        # Finally check global settings
        global_settings = self.load_global_settings()
        return global_settings.get(SETTING_BASE_URL) or global_settings.get(SETTING_API_URL)

    def get_api_key(self) -> Optional[str]:
        """Get API key from settings (checks project, user, global in order)."""
        # Check project .claude/settings.json first
        project = self.load_project_settings()
        if SETTING_API_KEY in project:
            return project[SETTING_API_KEY]

        # Check project .claude.json
        claude_json = self.load_claude_json()
        if SETTING_API_KEY in claude_json:
            return claude_json[SETTING_API_KEY]

        # Check user ~/.claude/settings.json
        user_settings = self.load_user_settings()
        if SETTING_API_KEY in user_settings:
            return user_settings[SETTING_API_KEY]

        # Check user ~/.claude.json
        user_claude_json = self.load_user_claude_json()
        if SETTING_API_KEY in user_claude_json:
            return user_claude_json[SETTING_API_KEY]

        # Finally check global settings
        global_settings = self.load_global_settings()
        return global_settings.get(SETTING_API_KEY)


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


def get_setting_model() -> Optional[str]:
    """Get model from settings."""
    return get_settings().get_model()


def get_setting_base_url() -> Optional[str]:
    """Get base URL from settings."""
    return get_settings().get_base_url()


def get_setting_api_key() -> Optional[str]:
    """Get API key from settings."""
    return get_settings().get_api_key()


__all__ = [
    "Settings",
    "get_settings",
    "get_setting",
    "set_setting",
    "get_setting_model",
    "get_setting_base_url",
    "get_setting_api_key",
    "get_claude_settings_path",
    "get_user_claude_settings_path",
    "get_user_claude_config_path",
    "get_claude_config_path",
    "get_global_settings_path",
    "load_json_file",
    "save_json_file",
]