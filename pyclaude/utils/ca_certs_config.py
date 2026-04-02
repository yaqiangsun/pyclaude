"""
CA certificates config utilities.

Apply NODE_EXTRA_CA_CERTS from settings.json to process.env early in init.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Placeholder for get_global_config
def _get_global_config() -> Optional[dict]:
    """Get global config placeholder."""
    return None


# Placeholder for get_settings_for_source
def _get_settings_for_source(source: str) -> Optional[dict]:
    """Get settings for source placeholder."""
    return None


def apply_extra_ca_certs_from_config() -> Optional[str]:
    """Apply NODE_EXTRA_CA_CERTS from settings.json to process.env.

    Must be called BEFORE any TLS connections are made.

    Returns:
        The applied certificate path, or None if not set
    """
    if os.environ.get("NODE_EXTRA_CA_CERTS"):
        return None  # Already set in environment

    config_path = _get_extra_certs_path_from_config()
    if config_path:
        os.environ["NODE_EXTRA_CA_CERTS"] = config_path
        logger.debug(
            f"CA certs: Applied NODE_EXTRA_CA_CERTS from config to process.env: {config_path}"
        )
        return config_path

    return None


def _get_extra_certs_path_from_config() -> Optional[str]:
    """Read NODE_EXTRA_CA_CERTS from settings/config as a fallback.

    Only reads from user-controlled settings (~/.claude/settings.json),
    not project-level settings, to prevent malicious projects from
    injecting CA certs before the trust dialog.
    """
    try:
        global_config = _get_global_config()
        global_env = global_config.get("env", {}) if global_config else {}

        settings = _get_settings_for_source("userSettings")
        settings_env = settings.get("env", {}) if settings else {}

        logger.debug(
            f"CA certs: Config fallback - globalEnv keys: {', '.join(global_env.keys()) if global_env else 'none'}, "
            f"settingsEnv keys: {', '.join(settings_env.keys()) if settings_env else 'none'}"
        )

        # Settings override global config
        path = settings_env.get("NODE_EXTRA_CA_CERTS") or global_env.get("NODE_EXTRA_CA_CERTS")
        if path:
            logger.debug(f"CA certs: Found NODE_EXTRA_CA_CERTS in config/settings: {path}")
        return path
    except Exception as error:
        logger.debug(f"CA certs: Config fallback failed: {error}")
        return None


__all__ = ["apply_extra_ca_certs_from_config"]