"""
Error log sink utilities.

Centralized error logging.
"""

from typing import Optional, Dict, Any
import logging


class ErrorLogSink:
    """Centralized error logging sink."""

    def __init__(self):
        self.errors: list = []

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an error with context.

        Args:
            error: Exception to log
            context: Additional context
        """
        self.errors.append({
            "error": str(error),
            "type": type(error).__name__,
            "context": context or {},
        })

    def get_errors(self) -> list:
        """Get all logged errors."""
        return self.errors

    def clear_errors(self) -> None:
        """Clear all errors."""
        self.errors.clear()


# Global sink instance
_error_sink = ErrorLogSink()


def get_error_sink() -> ErrorLogSink:
    """Get the global error sink."""
    return _error_sink


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error to the global sink."""
    _error_sink.log_error(error, context)


__all__ = [
    "ErrorLogSink",
    "get_error_sink",
    "log_error",
]