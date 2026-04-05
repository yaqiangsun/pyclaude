"""
Authentication utilities.
"""

import os
from typing import Optional, Tuple

from pyclaude.utils.settings import get_settings, SETTING_API_KEY, SETTING_ENV

# Safe env vars that can be applied from settings without trust dialog
SAFE_ENV_VARS = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION",
    "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_VERTEX_LOCATION",
    "ANTHROPIC_FOUNDRY_API_KEY",
    "ANTHROPIC_FOUNDRY_PROJECT_ID",
    "ANTHROPIC_FOUNDRY_LOCATION",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
}


def _apply_settings_env_to_process_env() -> None:
    """Apply environment variables from settings to process.env.

    This mirrors the logic in src/utils/managedEnv.ts where settings.env
    variables are applied to process.env so the code can read them like
    regular environment variables.
    """
    try:
        settings = get_settings()

        # Get all settings merged (user settings have higher priority)
        all_settings = settings.get_all()

        # Apply env block from settings to process.env
        if SETTING_ENV in all_settings and isinstance(all_settings[SETTING_ENV], dict):
            env_block = all_settings[SETTING_ENV]
            for key, value in env_block.items():
                if value is not None:
                    # Only apply safe env vars (like ANTHROPIC_API_KEY)
                    if key.upper() in SAFE_ENV_VARS:
                        # Only override if not already set in environment
                        if key not in os.environ:
                            os.environ[key] = str(value)
    except Exception:
        # If settings loading fails, silently continue
        pass


def get_anthropic_api_key() -> Optional[str]:
    """Get the Anthropic API key."""
    key, _ = get_anthropic_api_key_with_source()
    return key


def is_anthropic_auth_enabled() -> bool:
    """Check if Anthropic authentication is enabled."""
    return bool(get_anthropic_api_key())


def is_claude_ai_subscriber() -> bool:
    """Check if user is a Claude AI subscriber."""
    return os.environ.get("CLAUDE_AI_SUBSCRIBER", "").lower() == "true"


def get_anthropic_api_key_with_source(
    skip_retrieving_key_from_api_key_helper: bool = False,
) -> Tuple[Optional[str], str]:
    """Get Anthropic API key and its source.

    Priority:
    1. Settings files with apiKey field
    2. Settings env block (settings.env.ANTHROPIC_API_KEY) - applied to process.env
    3. Environment variables (ANTHROPIC_API_KEY, CLAUDE_API_KEY)

    Returns:
        Tuple of (api_key, source)
    """
    # First, apply settings.env to process.env (like src does)
    _apply_settings_env_to_process_env()

    # Check direct apiKey field in settings files
    try:
        settings = get_settings()

        # Check user ~/.claude/settings.json
        user_settings = settings.load_user_settings()
        if SETTING_API_KEY in user_settings:
            return user_settings[SETTING_API_KEY], "user_settings"

        # Check user ~/.claude.json
        user_claude_json = settings.load_user_claude_json()
        if SETTING_API_KEY in user_claude_json:
            return user_claude_json[SETTING_API_KEY], "user_claude_json"

        # Check project .claude/settings.json
        project_settings = settings.load_project_settings()
        if SETTING_API_KEY in project_settings:
            return project_settings[SETTING_API_KEY], "project_settings"

        # Check project .claude.json
        claude_json = settings.load_claude_json()
        if SETTING_API_KEY in claude_json:
            return claude_json[SETTING_API_KEY], "project_claude_json"

        # Check global settings
        global_settings = settings.load_global_settings()
        if SETTING_API_KEY in global_settings:
            return global_settings[SETTING_API_KEY], "global_settings"
    except Exception:
        # If settings loading fails, continue to other methods
        pass

    # Check environment variables (now includes settings.env values)
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
    if key:
        return key, "env"

    # Check config file (legacy method)
    config_key = os.environ.get("CLAUDE_API_KEY_FROM_CONFIG")
    if config_key:
        return config_key, "config"

    # Check apiKeyHelper (skipped by default for security)
    if not skip_retrieving_key_from_api_key_helper:
        helper_key = os.environ.get("CLAUDE_CODE_API_KEY_HELPER")
        if helper_key:
            return helper_key, "apiKeyHelper"

    return None, "none"


async def get_api_key_from_api_key_helper(is_non_interactive: bool) -> Optional[str]:
    """Get API key from the configured helper."""
    helper = os.environ.get("CLAUDE_CODE_API_KEY_HELPER")
    if not helper:
        return None

    # Execute the helper (placeholder - would run shell command)
    return None


__all__ = [
    "get_anthropic_api_key",
    "is_anthropic_auth_enabled",
    "is_claude_ai_subscriber",
    "get_anthropic_api_key_with_source",
    "get_api_key_from_api_key_helper",
]