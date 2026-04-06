"""Code session API."""

from typing import Dict, Any, Optional


class CodeSessionAPI:
    """API for code sessions."""

    def __init__(self, session_id: str, base_url: str):
        self.session_id = session_id
        self.base_url = base_url

    async def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            'session_id': self.session_id,
            'base_url': self.base_url,
            'status': 'active',
        }

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the session."""
        return {'success': True, 'message_id': message.get('id')}

    async def get_messages(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Get messages from the session."""
        return {'messages': [], 'has_more': False}


def create_code_session_api(session_id: str, base_url: str = 'https://api.anthropic.com') -> CodeSessionAPI:
    """Create a code session API instance."""
    return CodeSessionAPI(session_id, base_url)


__all__ = ['CodeSessionAPI', 'create_code_session_api']