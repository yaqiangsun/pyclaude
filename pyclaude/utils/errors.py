"""Error classes and utilities."""

from typing import Optional


class ClaudeError(Exception):
    """Base error class for Claude Code."""

    def __init__(self, message: str):
        super().__init__(message)
        self.name = self.__class__.__name__


class MalformedCommandError(ClaudeError):
    """Error for malformed commands."""
    pass


class AbortError(ClaudeError):
    """Error for aborted operations."""

    def __init__(self, message: str = ''):
        super().__init__(message)
        self.name = 'AbortError'


def is_abort_error(e: Exception) -> bool:
    """Check if error is an abort-shaped error."""
    return (
        isinstance(e, AbortError) or
        e.name == 'AbortError'
    )


class ConfigParseError(ClaudeError):
    """Error for configuration file parsing errors."""

    def __init__(self, message: str, file_path: str, default_config: dict):
        super().__init__(message)
        self.name = 'ConfigParseError'
        self.file_path = file_path
        self.default_config = default_config


class ShellError(ClaudeError):
    """Error for shell command failures."""

    def __init__(self, message: str, code: Optional[int] = None, stderr: Optional[str] = None):
        super().__init__(message)
        self.name = 'ShellError'
        self.code = code
        self.stderr = stderr


def is_enoent(e: Exception) -> bool:
    """Check if error is ENOENT (file not found)."""
    if hasattr(e, 'errno'):
        import errno
        return e.errno == errno.ENOENT
    return False


__all__ = [
    'ClaudeError',
    'MalformedCommandError',
    'AbortError',
    'ConfigParseError',
    'ShellError',
    'is_abort_error',
    'is_enoent',
]