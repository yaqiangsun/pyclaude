"""
Migration: Migrate first-party users off explicit Opus 4.0/4.1 model strings.

The 'opus' alias already resolves to Opus 4.6 for 1P, so anyone still
on an explicit 4.0/4.1 string pinned it in settings before 4.5 launched.
"""
import os
from typing import Any, Dict


# Legacy model strings to migrate
LEGACY_MODELS = [
    'claude-opus-4-20250514',
    'claude-opus-4-1-20250805',
    'claude-opus-4-0',
    'claude-opus-4-1',
]


def migrate_legacy_opus_to_current() -> None:
    """
    Migrate legacy Opus model strings to current 'opus' alias.
    """
    from ..services.analytics import log_event

    # Would check API provider
    api_provider = os.environ.get('API_PROVIDER', 'firstParty')
    if api_provider != 'firstParty':
        return

    # Would check if legacy model remap is enabled
    # if not isLegacyModelRemapEnabled():
    #     return

    # Would get user settings model
    # model = getSettingsForSource('userSettings')?.model

    # Only touch userSettings - leave project/local/policy alone
    # if model in LEGACY_MODELS:
    #     updateSettingsForSource('userSettings', {'model': 'opus'})

    log_event('tengu_migrate_legacy_opus_to_current', {})


__all__ = ['migrate_legacy_opus_to_current', 'LEGACY_MODELS']