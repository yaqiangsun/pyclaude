"""
Browser and path opening utilities.
"""

import os
import platform
import subprocess
from urllib.parse import urlparse


def validate_url(url: str) -> None:
    """Validate URL format and protocol.

    Args:
        url: The URL to validate

    Raises:
        ValueError: If URL is invalid or has wrong protocol
    """
    try:
        parsed_url = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {url}") from e

    # Validate URL protocol for security
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(
            f"Invalid URL protocol: must use http:// or https://, got {parsed_url.scheme}"
        )


def open_path(path: str) -> bool:
    """Open a file or folder path using the system's default handler.

    Uses `open` on macOS, `explorer` on Windows, `xdg-open` on Linux.

    Args:
        path: The path to open

    Returns:
        True if successful, False otherwise
    """
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(
                ["explorer", path],
                capture_output=True,
            )
            return result.returncode == 0
        command = "open" if system == "Darwin" else "xdg-open"
        result = subprocess.run(
            [command, path],
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def open_browser(url: str) -> bool:
    """Open a URL in the default browser.

    Args:
        url: The URL to open

    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse and validate the URL
        validate_url(url)

        browser_env = os.environ.get("BROWSER")
        system = platform.system()

        if system == "Windows":
            if browser_env:
                # browsers require shell, else they will treat this as a file:/// handle
                result = subprocess.run(
                    [browser_env, f'"{url}"'],
                    capture_output=True,
                    shell=True,
                )
                return result.returncode == 0
            result = subprocess.run(
                ["rundll32", "url,OpenURL", url],
                capture_output=True,
            )
            return result.returncode == 0
        else:
            command = browser_env or ("open" if system == "Darwin" else "xdg-open")
            result = subprocess.run(
                [command, url],
                capture_output=True,
            )
            return result.returncode == 0
    except Exception:
        return False


__all__ = ["validate_url", "open_path", "open_browser"]