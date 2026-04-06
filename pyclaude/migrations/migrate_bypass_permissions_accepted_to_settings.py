"""
Migration: Move bypassPermissionsAccepted preference to settings.json.
"""
import os


def migrate_bypass_permissions_accepted_to_settings() -> None:
    """
    Migrate bypassPermissionsAccepted to settings.
    """
    # Would get global config and migrate
    pass


__all__ = ['migrate_bypass_permissions_accepted_to_settings']