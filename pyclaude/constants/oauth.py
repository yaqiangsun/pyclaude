"""OAuth constants."""

from typing import Dict


# OAuth configuration
OAUTH_CLIENT_ID = 'claude-cli'
OAUTH_AUTHORIZATION_ENDPOINT = 'https://auth.anthropic.com/oauth/authorize'
OAUTH_TOKEN_ENDPOINT = 'https://auth.anthropic.com/oauth/token'
OAUTH_SCOPES = ['profile', 'email', 'read', 'write']

# Profile scopes
CLAUDE_AI_PROFILE_SCOPE = 'profile:read'
CLAUDE_AI_EMAIL_SCOPE = 'email:read'

# Token settings
TOKEN_REFRESH_BEFORE_SECONDS = 300  # 5 minutes before expiry
TOKEN_MAX_REFRESH_RETRIES = 3


# OAuth grant types
GRANT_AUTHORIZATION_CODE = 'authorization_code'
GRANT_REFRESH_TOKEN = 'refresh_token'


def get_oauth_config() -> Dict[str, str]:
    """Get OAuth configuration."""
    return {
        'client_id': OAUTH_CLIENT_ID,
        'authorization_endpoint': OAUTH_AUTHORIZATION_ENDPOINT,
        'token_endpoint': OAUTH_TOKEN_ENDPOINT,
        'scopes': ' '.join(OAUTH_SCOPES),
    }


__all__ = [
    'OAUTH_CLIENT_ID',
    'OAUTH_AUTHORIZATION_ENDPOINT',
    'OAUTH_TOKEN_ENDPOINT',
    'OAUTH_SCOPES',
    'CLAUDE_AI_PROFILE_SCOPE',
    'CLAUDE_AI_EMAIL_SCOPE',
    'TOKEN_REFRESH_BEFORE_SECONDS',
    'TOKEN_MAX_REFRESH_RETRIES',
    'GRANT_AUTHORIZATION_CODE',
    'GRANT_REFRESH_TOKEN',
    'get_oauth_config',
]