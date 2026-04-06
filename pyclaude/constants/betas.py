"""Beta features configuration."""

from typing import Dict, List


# Beta features
BETA_FEATURES: Dict[str, bool] = {
    'claude': True,
    'mcp': True,
    'codeium': False,
}


def is_beta_enabled(beta: str) -> bool:
    """Check if a beta feature is enabled."""
    return BETA_FEATURES.get(beta, False)


def should_include_first_party_only_betas() -> bool:
    """Check if should include first-party only betas."""
    return True


def get_enabled_betas() -> List[str]:
    """Get list of enabled beta features."""
    return [b for b, enabled in BETA_FEATURES.items() if enabled]


__all__ = ['BETA_FEATURES', 'is_beta_enabled', 'should_include_first_party_only_betas', 'get_enabled_betas']