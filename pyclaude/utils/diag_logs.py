"""
Diagnostic logging utilities.

Logs diagnostic information to a logfile. This information is sent
via the environment manager to session-ingress to monitor issues.

IMPORTANT - this function MUST NOT be called with any PII, including
file paths, project names, repo names, prompts, etc.
"""

import os
import json
from typing import Optional, Dict, Any, Callable
from datetime import datetime

# Type aliases
DiagnosticLogLevel = str  # 'debug' | 'info' | 'warn' | 'error'


def _get_diagnostic_log_file() -> Optional[str]:
    """Get the diagnostic log file path."""
    return os.environ.get("CLAUDE_CODE_DIAGNOSTICS_FILE")


def log_for_diagnostics_no_pii(
    level: DiagnosticLogLevel,
    event: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Log diagnostic information without PII.

    Args:
        level: Log level (debug, info, warn, error)
        event: A specific event: "started", "mcp_connected", etc.
        data: Optional additional data to log
    """
    log_file = _get_diagnostic_log_file()
    if not log_file:
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "event": event,
        "data": data or {},
    }

    line = json.dumps(entry) + "\n"

    try:
        # Try append first
        with open(log_file, "a") as f:
            f.write(line)
    except FileNotFoundError:
        # Try creating the directory first
        try:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            with open(log_file, "a") as f:
                f.write(line)
        except Exception:
            # Silently fail if logging is not possible
            pass
    except Exception:
        # Silently fail
        pass


async def with_diagnostics_timing(
    event: str,
    fn: Callable,
    get_data: Optional[Callable[[Any], Dict[str, Any]]] = None,
) -> Any:
    """Wrap an async function with diagnostic timing logs.

    Logs `{event}_started` before execution and `{event}_completed` after with duration_ms.

    Args:
        event: Event name prefix (e.g., "git_status" -> logs "git_status_started" and "git_status_completed")
        fn: Async function to execute and time
        get_data: Optional function to extract additional data from the result

    Returns:
        The result of the wrapped function
    """
    import time
    start_time = time.time() * 1000
    log_for_diagnostics_no_pii("info", f"{event}_started")

    try:
        result = await fn()
        additional_data = get_data(result) if get_data else {}
        log_for_diagnostics_no_pii("info", f"{event}_completed", {
            "duration_ms": int(time.time() * 1000 - start_time),
            **additional_data,
        })
        return result
    except Exception:
        log_for_diagnostics_no_pii("error", f"{event}_failed", {
            "duration_ms": int(time.time() * 1000 - start_time),
        })
        raise


__all__ = [
    "DiagnosticLogLevel",
    "log_for_diagnostics_no_pii",
    "with_diagnostics_timing",
]