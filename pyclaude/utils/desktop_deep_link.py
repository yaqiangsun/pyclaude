"""
Desktop deep link utilities.

Build and open deep links to resume sessions in Claude Desktop.
"""

import os
import platform
import subprocess
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass

MIN_DESKTOP_VERSION = "1.1.2396"


def _is_dev_mode() -> bool:
    """Check if running in dev mode."""
    if os.environ.get("NODE_ENV") == "development":
        return True

    # Check build directories
    paths_to_check = [os.environ.get("argv1", ""), os.environ.get("PYTHONPATH", "")]
    build_dirs = ["/build-ant/", "/build-ant-native/", "/build-external/"]

    return any(any(d in p for d in build_dirs) for p in paths_to_check)


def build_desktop_deep_link(session_id: str, cwd: str = "") -> str:
    """Build a deep link URL for Claude Desktop to resume a CLI session.

    Format: claude://resume?session={sessionId}&cwd={cwd}

    Args:
        session_id: Session ID to resume
        cwd: Current working directory

    Returns:
        Deep link URL
    """
    protocol = "claude-dev" if _is_dev_mode() else "claude"
    url = f"{protocol}://resume?session={session_id}"
    if cwd:
        url += f"&cwd={cwd}"
    return url


async def is_desktop_installed() -> bool:
    """Check if Claude Desktop app is installed.

    Returns:
        True if Desktop is installed
    """
    if _is_dev_mode():
        return True

    system = platform.system()

    if system == "Darwin":
        return os.path.exists("/Applications/Claude.app")
    elif system == "Linux":
        try:
            result = subprocess.run(
                ["xdg-mime", "query", "default", "x-scheme-handler/claude"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip()
        except Exception:
            return False
    elif system == "Windows":
        try:
            result = subprocess.run(
                ["reg", "query", "HKEY_CLASSES_ROOT\\claude"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    return False


async def get_desktop_version() -> Optional[str]:
    """Detect the installed Claude Desktop version.

    Returns:
        Version string or None
    """
    system = platform.system()

    if system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "/Applications/Claude.app/Contents/Info.plist", "CFBundleShortVersionString"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return version if version else None
        except Exception:
            pass
    elif system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            install_dir = os.path.join(local_app_data, "AnthropicClaude")
            try:
                entries = os.listdir(install_dir)
                versions = [e[4:] for e in entries if e.startswith("app-")]
                if versions:
                    return sorted(versions)[-1]
            except Exception:
                pass

    return None


@dataclass
class DesktopInstallStatus:
    """Desktop install status."""
    status: str  # 'not-installed' | 'version-too-old' | 'ready'
    version: Optional[str] = None


async def get_desktop_install_status() -> DesktopInstallStatus:
    """Check Desktop install status including version compatibility.

    Returns:
        DesktopInstallStatus
    """
    installed = await is_desktop_installed()
    if not installed:
        return DesktopInstallStatus(status="not-installed")

    try:
        version = await get_desktop_version()
    except Exception:
        return DesktopInstallStatus(status="ready", version="unknown")

    if not version:
        return DesktopInstallStatus(status="ready", version="unknown")

    # Simple version check - in real impl would use semver
    return DesktopInstallStatus(status="ready", version=version)


async def open_deep_link(deep_link_url: str) -> bool:
    """Open a deep link URL using the platform-specific mechanism.

    Args:
        deep_link_url: Deep link URL to open

    Returns:
        True if successful
    """
    system = platform.system()

    if system == "Darwin":
        result = subprocess.run(["open", deep_link_url], capture_output=True)
        return result.returncode == 0
    elif system == "Linux":
        result = subprocess.run(["xdg-open", deep_link_url], capture_output=True)
        return result.returncode == 0
    elif system == "Windows":
        result = subprocess.run(["cmd", "/c", "start", "", deep_link_url], capture_output=True)
        return result.returncode == 0

    return False


async def open_current_session_in_desktop(
    session_id: str,
    cwd: str = "",
) -> Dict[str, Any]:
    """Build and open a deep link to resume the current session in Claude Desktop.

    Args:
        session_id: Session ID to resume
        cwd: Current working directory

    Returns:
        Dict with success status and any error message
    """
    # Check if Desktop is installed
    installed = await is_desktop_installed()
    if not installed:
        return {
            "success": False,
            "error": "Claude Desktop is not installed. Install it from https://claude.ai/download",
        }

    # Build and open the deep link
    deep_link_url = build_desktop_deep_link(session_id, cwd)
    opened = await open_deep_link(deep_link_url)

    if not opened:
        return {
            "success": False,
            "error": "Failed to open Claude Desktop. Please try opening it manually.",
            "deepLinkUrl": deep_link_url,
        }

    return {"success": True, "deepLinkUrl": deep_link_url}


__all__ = [
    "DesktopInstallStatus",
    "build_desktop_deep_link",
    "is_desktop_installed",
    "get_desktop_version",
    "get_desktop_install_status",
    "open_deep_link",
    "open_current_session_in_desktop",
]