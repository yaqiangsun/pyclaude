"""BTW command - by the way."""
from typing import Any, Dict

async def execute(args: str, context: Dict[str, Any]) -> Dict[str, str]:
    return {'type': 'text', 'value': 'BTW: ' + args}

call = execute
CONFIG = {'type': 'local', 'name': 'btw', 'description': 'By the way'}
__all__ = ['call', 'execute', 'CONFIG']