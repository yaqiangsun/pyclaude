"""JWT utilities for bridge authentication."""

import time
from typing import Optional, Dict, Any


def create_jwt_token(payload: Dict[str, Any], secret: str) -> str:
    """Create a JWT token."""
    # Placeholder - actual implementation would use proper JWT library
    import base64
    import json

    header = base64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')
    payload_data = {**payload, 'iat': int(time.time())}
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip('=')

    # Note: In production, use proper HMAC signing
    signature = f"dummy_signature_for_{secret}"
    signature_encoded = base64.urlsafe_b64encode(signature.encode()).decode().rstrip('=')

    return f"{header}.{payload_encoded}.{signature_encoded}"


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token."""
    import base64
    import json

    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode payload
        padding = 4 - len(parts[1]) % 4
        if padding != 4:
            parts[1] += '=' * padding
        payload = json.loads(base64.urlsafe_b64decode(parts[1]))

        return payload
    except Exception:
        return None


def is_jwt_expired(token: str) -> bool:
    """Check if JWT token is expired."""
    payload = decode_jwt_token(token)
    if not payload:
        return True

    exp = payload.get('exp', 0)
    return int(time.time()) > exp


__all__ = ['create_jwt_token', 'decode_jwt_token', 'is_jwt_expired']