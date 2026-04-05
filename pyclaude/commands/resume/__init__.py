"""Command."""
from typing import Any, Dict

async def execute(args: str, context: Dict[str, Any]) -> Dict[str, str]:
    return {'type': 'text', 'value': 'OK'}

call = execute
CONFIG = {'type': 'local', 'name': 'command', 'description': 'Command'}
__all__ = ['call', 'execute', 'CONFIG']
