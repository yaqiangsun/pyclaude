"""Plugins command package."""

from .plugins import call, execute, CONFIG

# Add aliases to match src
CONFIG['aliases'] = ['plugin', 'marketplace']

__all__ = ['call', 'execute', 'CONFIG']