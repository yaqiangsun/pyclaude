"""
IDE integration utilities.

Detect and interact with IDEs.
"""

import os
import subprocess
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class IDEType(str, Enum):
    """Supported IDEs."""
    VSCODE = "vscode"
    JETBRAINS = "jetbrains"
    SUBLIME = "sublime"
    ATOM = "atom"
    VIM = "vim"
    EMACS = "emacs"
    UNKNOWN = "unknown"


@dataclass
class IDEInfo:
    """IDE information."""
    type: IDEType
    name: str
    path: Optional[str] = None
    version: Optional[str] = None


def detect_ide() -> Optional[IDEInfo]:
    """Detect installed IDE.

    Returns:
        IDE info or None
    """
    # Check common IDE paths
    if os.path.exists("/Applications/Visual Studio Code.app"):
        return IDEInfo(type=IDEType.VSCODE, name="Visual Studio Code")

    if os.environ.get("VSCODE_INJECTION"):
        return IDEInfo(type=IDEType.VSCODE, name="VSCode (injected)")

    return None


def get_ide_path(ide_type: IDEType) -> Optional[str]:
    """Get IDE executable path.

    Args:
        ide_type: IDE type

    Returns:
        Path to IDE or None
    """
    paths = {
        IDEType.VSCODE: [
            "/Applications/Visual Studio Code.app/Contents/MacOS/Electron",
            "/usr/bin/code",
        ],
    }

    for path in paths.get(ide_type, []):
        if os.path.exists(path):
            return path

    return None


def open_in_ide(path: str, ide: Optional[IDEType] = None) -> bool:
    """Open file/folder in IDE.

    Args:
        path: File or directory path
        ide: IDE to use (auto-detect if None)

    Returns:
        True if successful
    """
    if ide is None:
        detected = detect_ide()
        if detected:
            ide = detected.type

    if ide == IDEType.VSCODE:
        try:
            subprocess.run(["code", path], capture_output=True)
            return True
        except Exception:
            pass

    return False


__all__ = [
    "IDEType",
    "IDEInfo",
    "detect_ide",
    "get_ide_path",
    "open_in_ide",
]