"""
Migration: Move user-set autoUpdates preference to settings.json env var
Only migrates if user explicitly disabled auto-updates (not for protection)
This preserves user intent while allowing native installations to auto-update
"""
import os
from typing import Any, Dict


def migrate_auto_updates_to_settings() -> None:
    """
    Migrate autoUpdates preference to settings.json env var.
    """
    from ..services.analytics import log_event

    # Would get global config in full implementation
    auto_updates = os.environ.get('AUTO_UPDATES')
    auto_updates_protected = os.environ.get('AUTO_UPDATES_PROTECTED_FOR_NATIVE')

    # Only migrate if autoUpdates was explicitly set to false by user preference
    # (not automatically for native protection)
    if auto_updates != 'false' or auto_updates_protected == 'true':
        return

    try:
        # Would get user settings
        user_settings = {}  # getSettingsForSource('userSettings')

        # Always set DISABLE_AUTOUPDATER to preserve user intent
        user_settings.setdefault('env', {})
        user_settings['env']['DISABLE_AUTOUPDATER'] = '1'

        # Would update settings
        # updateSettingsForSource('userSettings', user_settings)

        log_event('tengu_migrate_autoupdates_to_settings', {
            'was_user_preference': True,
            'already_had_env_var': 'DISABLE_AUTOUPDATER' in user_settings.get('env', {}),
        })

        # Set env var immediately
        os.environ['DISABLE_AUTOUPDATER'] = '1'

        # Would remove autoUpdates from global config after successful migration

    except Exception as error:
        # Would log error
        pass


__all__ = ['migrate_auto_updates_to_settings']