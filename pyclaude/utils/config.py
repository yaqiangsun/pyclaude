"""
Configuration management.

Handles global and project-level configuration.
"""

import os
import json
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path


# Type aliases
ReleaseChannel = str  # 'stable' | 'latest'
InstallMethod = str  # 'local' | 'native' | 'global' | 'unknown'
ThemeSetting = str  # 'dark' | 'light'


@dataclass
class ProjectConfig:
    """Project-level configuration."""
    allowed_tools: list = field(default_factory=list)
    mcp_context_uris: list = field(default_factory=list)
    mcp_servers: Dict[str, Any] = field(default_factory=dict)
    has_trust_dialog_accepted: bool = False
    has_completed_project_onboarding: bool = False
    project_onboarding_seen_count: int = 0
    enabled_mcpjson_servers: list = field(default_factory=list)
    disabled_mcpjson_servers: list = field(default_factory=list)
    disabled_mcp_servers: list = field(default_factory=list)
    enabled_mcp_servers: list = field(default_factory=list)


@dataclass
class GlobalConfig:
    """Global configuration."""
    num_startups: int = 0
    install_method: Optional[InstallMethod] = None
    auto_updates: Optional[bool] = None
    theme: ThemeSetting = "dark"
    has_completed_onboarding: bool = False
    verbose: bool = False
    editor_mode: str = "normal"
    auto_compact_enabled: bool = True
    show_turn_duration: bool = True
    env: Dict[str, str] = field(default_factory=dict)
    tips_history: Dict[str, int] = field(default_factory=dict)
    memory_usage_count: int = 0
    prompt_queue_use_count: int = 0
    todo_feature_enabled: bool = True
    show_expanded_todos: bool = False
    message_idle_notif_threshold_ms: int = 60000
    auto_connect_ide: bool = False
    auto_install_ide_extension: bool = True
    file_checkpointing_enabled: bool = True
    terminal_progress_bar_enabled: bool = True
    preferred_notif_channel: str = "auto"
    cached_statsig_gates: Dict[str, bool] = field(default_factory=dict)
    cached_dynamic_configs: Dict[str, Any] = field(default_factory=dict)
    cached_growth_book_features: Dict[str, Any] = field(default_factory=dict)
    respect_gitignore: bool = True
    copy_full_response: bool = False
    projects: Dict[str, ProjectConfig] = field(default_factory=dict)
    oauth_account: Optional[Dict[str, Any]] = None
    custom_api_key_responses: Dict[str, list] = field(default_factory=lambda: {"approved": [], "rejected": []})


# Default config
DEFAULT_GLOBAL_CONFIG = GlobalConfig()
DEFAULT_PROJECT_CONFIG = ProjectConfig()

# In-memory cache
_global_config_cache: Optional[GlobalConfig] = None


def get_claude_config_home_dir() -> str:
    """Get the Claude config home directory."""
    return os.environ.get("CLAUDE_CONFIG_HOME", os.path.expanduser("~/.config/claude"))


def get_global_claude_file() -> str:
    """Get the global config file path."""
    return os.path.join(get_claude_config_home_dir(), "settings.json")


def get_global_config() -> GlobalConfig:
    """Get the global configuration."""
    global _global_config_cache

    if _global_config_cache is not None:
        return _global_config_cache

    config_file = get_global_claude_file()

    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                _global_config_cache = GlobalConfig(**data)
                return _global_config_cache
    except Exception:
        pass

    _global_config_cache = GlobalConfig()
    return _global_config_cache


def save_global_config(updater: Callable[[GlobalConfig], GlobalConfig]) -> None:
    """Update global configuration."""
    global _global_config_cache

    current = get_global_config()
    updated = updater(current)

    config_file = get_global_claude_file()
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    try:
        with open(config_file, "w") as f:
            json.dump(updated.__dict__, f, indent=2)
        _global_config_cache = updated
    except Exception:
        pass


def get_current_project_config() -> ProjectConfig:
    """Get project configuration for current directory."""
    config = get_global_config()
    cwd = os.getcwd()

    if cwd in config.projects:
        return config.projects[cwd]

    return ProjectConfig()


def save_current_project_config(
    updater: Callable[[ProjectConfig], ProjectConfig]
) -> None:
    """Update project configuration."""
    cwd = os.getcwd()

    def update_config(config: GlobalConfig) -> GlobalConfig:
        current_project = config.projects.get(cwd, ProjectConfig())
        updated_project = updater(current_project)
        config.projects[cwd] = updated_project
        return config

    save_global_config(update_config)


def is_auto_updater_disabled() -> bool:
    """Check if auto-updater is disabled."""
    config = get_global_config()
    return config.auto_updates is False


def get_or_create_user_id() -> str:
    """Get or create a user ID."""
    config = get_global_config()

    # Would generate random ID if not exists
    return ""


def normalize_path_for_config_key(path: str) -> str:
    """Normalize path for consistent JSON key lookup."""
    return os.path.normpath(path).replace("\\", "/")


__all__ = [
    "GlobalConfig",
    "ProjectConfig",
    "ReleaseChannel",
    "InstallMethod",
    "ThemeSetting",
    "DEFAULT_GLOBAL_CONFIG",
    "DEFAULT_PROJECT_CONFIG",
    "get_global_config",
    "save_global_config",
    "get_current_project_config",
    "save_current_project_config",
    "is_auto_updater_disabled",
    "get_or_create_user_id",
    "normalize_path_for_config_key",
    "get_claude_config_home_dir",
    "get_global_claude_file",
]