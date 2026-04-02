"""
Proxy utilities.

HTTP proxy configuration.
"""

import os
from typing import Optional, Dict


def get_proxy_settings() -> Dict[str, Optional[str]]:
    """Get HTTP proxy settings.

    Returns:
        Dict with http/https proxy
    """
    return {
        "http": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy"),
        "https": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"),
        "no_proxy": os.environ.get("NO_PROXY") or os.environ.get("no_proxy"),
    }


def is_proxy_enabled() -> bool:
    """Check if proxy is configured.

    Returns:
        True if proxy is set
    """
    settings = get_proxy_settings()
    return bool(settings["http"] or settings["https"])


def get_no_proxy_list() -> List[str]:
    """Get no-proxy hosts.

    Returns:
        List of hosts to bypass proxy
    """
    no_proxy = os.environ.get("NO_PROXY", "") or os.environ.get("no_proxy", "")
    return [h.strip() for h in no_proxy.split(",") if h.strip()]


def should_bypass_proxy(host: str) -> bool:
    """Check if host should bypass proxy.

    Args:
        host: Hostname

    Returns:
        True if should bypass
    """
    no_proxy = get_no_proxy_list()
    return host in no_proxy or "*" in no_proxy


__all__ = [
    "get_proxy_settings",
    "is_proxy_enabled",
    "get_no_proxy_list",
    "should_bypass_proxy",
]