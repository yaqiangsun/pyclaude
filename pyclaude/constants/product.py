"""Product constants."""

from typing import Dict


# Product info
PRODUCT_NAME = 'Claude Code'
PRODUCT_VERSION = '0.1.0'
PRODUCT_URL = 'https://claude.ai/code'

# Edition types
EDITION_FREE = 'free'
EDITION_PRO = 'pro'
EDITION_MAX = 'max'
EDITION_TEAM = 'team'

# Feature flags by edition
EDITION_FEATURES: Dict[str, list] = {
    EDITION_FREE: ['basic_chat', 'file_read', 'glob', 'grep'],
    EDITION_PRO: ['basic_chat', 'file_read', 'file_write', 'edit', 'glob', 'grep', 'mcp', 'agents'],
    EDITION_MAX: ['basic_chat', 'file_read', 'file_write', 'edit', 'glob', 'grep', 'mcp', 'agents', 'unlimited'],
    EDITION_TEAM: ['basic_chat', 'file_read', 'file_write', 'edit', 'glob', 'grep', 'mcp', 'agents', 'team'],
}


def get_product_name() -> str:
    """Get product name."""
    return PRODUCT_NAME


def get_product_version() -> str:
    """Get product version."""
    return PRODUCT_VERSION


def has_feature(edition: str, feature: str) -> bool:
    """Check if edition has a feature."""
    return feature in EDITION_FEATURES.get(edition, [])


__all__ = [
    'PRODUCT_NAME',
    'PRODUCT_VERSION',
    'PRODUCT_URL',
    'EDITION_FREE',
    'EDITION_PRO',
    'EDITION_MAX',
    'EDITION_TEAM',
    'EDITION_FEATURES',
    'get_product_name',
    'get_product_version',
    'has_feature',
]