"""Clear command - clear conversation history."""
from typing import Any, Dict


async def execute(args: str, context: Dict[str, Any]) -> Dict[str, str]:
    """Clear conversation history."""
    return {'type': 'text', 'value': 'Conversation cleared'}


call = execute
CONFIG = {'type': 'local', 'name': 'clear', 'description': 'Clear conversation'}
__all__ = ['call', 'execute', 'CONFIG']