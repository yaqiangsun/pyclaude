"""
API preconnect utilities.

Preconnect to the Anthropic API to overlap TCP+TLS handshake with startup.
"""

import os
from typing import Optional


_fired = False


def is_env_truthy(env_var: Optional[str]) -> bool:
    """Check if environment variable is truthy."""
    if not env_var:
        return False
    return env_var.lower() in ("1", "true", "yes", "on")


def preconnect_anthropic_api() -> None:
    """Preconnect to the Anthropic API to warm up the connection pool.

    Skipped when:
    - proxy/mTLS/unix socket configured
    - Bedrock/Vertex/Foundry configured
    """
    global _fired
    if _fired:
        return
    _fired = True

    # Skip if using a cloud provider
    if (
        is_env_truthy(os.environ.get("CLAUDE_CODE_USE_BEDROCK"))
        or is_env_truthy(os.environ.get("CLAUDE_CODE_USE_VERTEX"))
        or is_env_truthy(os.environ.get("CLAUDE_CODE_USE_FOUNDRY"))
    ):
        return

    # Skip if proxy/mTLS/unix
    if (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
        or os.environ.get("ANTHROPIC_UNIX_SOCKET")
        or os.environ.get("CLAUDE_CODE_CLIENT_CERT")
        or os.environ.get("CLAUDE_CODE_CLIENT_KEY")
    ):
        return

    # Use configured base URL
    base_url = os.environ.get("ANTHROPIC_BASE_URL")

    # Fire and forget - in Python we'd use httpx or similar
    # This is a placeholder - actual implementation would use async HTTP
    try:
        import httpx

        def make_request():
            try:
                client = httpx.Client(timeout=10.0)
                client.head(base_url or "https://api.anthropic.com")
                client.close()
            except Exception:
                pass

        # Would run in background thread
        # For now, just mark as fired
        pass
    except ImportError:
        pass


__all__ = [
    "preconnect_anthropic_api",
]