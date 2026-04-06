"""
Diagnostic tracking service for monitoring code diagnostics (errors, warnings, etc.)
"""
from typing import List, Optional, Dict, Any, Protocol
from dataclasses import dataclass, field
from enum import Enum


class DiagnosticSeverity(Enum):
    """Severity levels for diagnostics."""
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"
    HINT = "Hint"


@dataclass
class Diagnostic:
    """A single diagnostic message."""
    message: str
    severity: DiagnosticSeverity
    start_line: int
    start_character: int
    end_line: int
    end_character: int
    source: Optional[str] = None
    code: Optional[str] = None

    @property
    def range(self) -> Dict[str, Any]:
        return {
            'start': {'line': self.start_line, 'character': self.start_character},
            'end': {'line': self.end_line, 'character': self.end_character},
        }


@dataclass
class DiagnosticFile:
    """Diagnostics for a single file."""
    uri: str
    diagnostics: List[Diagnostic] = field(default_factory=list)


# Severity symbols for display
SEVERITY_SYMBOLS = {
    DiagnosticSeverity.ERROR: '✖',
    DiagnosticSeverity.WARNING: '⚠',
    DiagnosticSeverity.INFO: 'ℹ',
    DiagnosticSeverity.HINT: '★',
}

MAX_DIAGNOSTICS_SUMMARY_CHARS = 4000


class DiagnosticTrackingService:
    """Service for tracking code diagnostics before and after edits."""

    _instance: Optional['DiagnosticTrackingService'] = None

    def __new__(cls) -> 'DiagnosticTrackingService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.baseline: Dict[str, List[Diagnostic]] = {}
        self.right_file_diagnostics_state: Dict[str, List[Diagnostic]] = {}
        self.last_processed_timestamps: Dict[str, float] = {}
        self.mcp_client = None
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'DiagnosticTrackingService':
        """Get the singleton instance."""
        return cls()

    def initialize(self, mcp_client: Any) -> None:
        """Initialize the service with an MCP client."""
        if self._initialized:
            return
        self.mcp_client = mcp_client
        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the service."""
        self._initialized = False
        self.baseline.clear()
        self.right_file_diagnostics_state.clear()
        self.last_processed_timestamps.clear()

    def reset(self) -> None:
        """Reset tracking state while keeping the service initialized."""
        self.baseline.clear()
        self.right_file_diagnostics_state.clear()
        self.last_processed_timestamps.clear()

    def normalize_file_uri(self, file_uri: str) -> str:
        """Normalize a file URI by removing protocol prefixes."""
        prefixes = ['file://', '_claude_fs_right:', '_claude_fs_left:']
        normalized = file_uri
        for prefix in prefixes:
            if file_uri.startswith(prefix):
                normalized = file_uri[len(prefix):]
                break
        # Normalize path separators and handle case sensitivity
        import os
        normalized = os.path.normpath(normalized)
        return normalized

    async def before_file_edited(self, file_path: str) -> None:
        """Capture baseline diagnostics before editing a file."""
        if not self._initialized or not self.mcp_client:
            return

        timestamp = self._get_timestamp()
        normalized_path = self.normalize_file_uri(file_path)

        # In full implementation, would call MCP to get diagnostics
        # For now, just store empty baseline
        self.baseline[normalized_path] = []
        self.last_processed_timestamps[normalized_path] = timestamp

    async def get_new_diagnostics(self) -> List[DiagnosticFile]:
        """Get new diagnostics that aren't in the baseline."""
        if not self._initialized or not self.mcp_client:
            return []

        # In full implementation, would fetch diagnostics from MCP
        return []

    @staticmethod
    def format_diagnostics_summary(files: List[DiagnosticFile]) -> str:
        """Format diagnostics into a human-readable summary."""
        truncation_marker = '…[truncated]'
        result_lines = []

        for file in files:
            filename = file.uri.split('/')[-1] if '/' in file.uri else file.uri
            diag_lines = []
            for d in file.diagnostics:
                symbol = SEVERITY_SYMBOLS.get(d.severity, '•')
                location = f"[Line {d.start_line + 1}:{d.start_character + 1}]"
                code_part = f" [{d.code}]" if d.code else ""
                source_part = f" ({d.source})" if d.source else ""
                diag_lines.append(f"  {symbol} {location} {d.message}{code_part}{source_part}")

            result_lines.append(f"{filename}:\n" + "\n".join(diag_lines))

        result = "\n\n".join(result_lines)

        if len(result) > MAX_DIAGNOSTICS_SUMMARY_CHARS:
            result = result[:MAX_DIAGNOSTICS_SUMMARY_CHARS - len(truncation_marker)] + truncation_marker

        return result

    @staticmethod
    def get_severity_symbol(severity: DiagnosticSeverity) -> str:
        """Get the symbol for a diagnostic severity."""
        return SEVERITY_SYMBOLS.get(severity, '•')

    @staticmethod
    def _get_timestamp() -> float:
        """Get current timestamp."""
        import time
        return time.time()

    @staticmethod
    def are_diagnostics_equal(a: Diagnostic, b: Diagnostic) -> bool:
        """Check if two diagnostics are equal."""
        return (
            a.message == b.message and
            a.severity == b.severity and
            a.source == b.source and
            a.code == b.code and
            a.range == b.range
        )


# Singleton instance
diagnostic_tracker = DiagnosticTrackingService.get_instance()


__all__ = [
    'DiagnosticTrackingService',
    'Diagnostic',
    'DiagnosticFile',
    'DiagnosticSeverity',
    'diagnostic_tracker',
    'SEVERITY_SYMBOLS',
]