# Bash Tool Result Message - Render bash command results
# Reference: src/tools/BashTool/BashToolResultMessage.tsx

from typing import Any, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class BashOutput:
    """Output from bash command execution"""
    stdout: str
    stderr: str
    exit_code: int
    command: str
    truncated: bool = False
    interrupted: bool = False


# Pattern to match "Shell cwd was reset to <path>" message
SHELL_CWD_RESET_PATTERN = re.compile(r'(?:^|\n)(Shell cwd was reset to .+)$')

# Pattern to extract sandbox violations
SANDBOX_VIOLATIONS_PATTERN = re.compile(r'<sandbox_violations>([\s\S]*?)</sandbox_violations>')


def extract_sandbox_violations(stderr: str) -> Dict[str, str]:
    """Extracts sandbox violations from stderr if present"""
    violations_match = SANDBOX_VIOLATIONS_PATTERN.search(stderr)
    if not violations_match:
        return {"cleaned_stderr": stderr}

    # Remove the sandbox violations section from stderr
    cleaned_stderr = re.sub(SANDBOX_VIOLATIONS_PATTERN, '', stderr).strip()
    return {
        "cleaned_stderr": cleaned_stderr,
        "violations": violations_match.group(1)
    }


def extract_cwd_reset_warning(stderr: str) -> Dict[str, Any]:
    """Extracts the 'Shell cwd was reset' warning message from stderr"""
    match = SHELL_CWD_RESET_PATTERN.search(stderr)
    if not match:
        return {"cleaned_stderr": stderr, "cwd_reset_warning": None}

    cleaned_stderr = SHELL_CWD_RESET_PATTERN.sub('', stderr).strip()
    return {
        "cleaned_stderr": cleaned_stderr,
        "cwd_reset_warning": match.group(1)
    }


def render_tool_result_message(
    output: BashOutput,
    verbose: bool = False,
    timeout_ms: Optional[int] = None
) -> str:
    """Render the bash tool result message"""

    # Extract warnings from stderr
    cwd_warning = extract_cwd_reset_warning(output.stderr)
    sandbox_info = extract_sandbox_violations(output.stderr)

    cleaned_stderr = cwd_warning.get("cleaned_stderr", output.stderr)

    # Build result string
    lines = []

    # Add stdout if present
    if output.stdout:
        if verbose:
            lines.append(output.stdout)
        else:
            # Truncate long output
            max_lines = 100
            stdout_lines = output.stdout.split('\n')
            if len(stdout_lines) > max_lines:
                lines.append('\n'.join(stdout_lines[:max_lines]))
                lines.append(f"... ({len(stdout_lines) - max_lines} more lines)")
            else:
                lines.append(output.stdout)

    # Add stderr if present
    if cleaned_stderr:
        lines.append(f"[stderr] {cleaned_stderr}")

    # Add exit code if non-zero
    if output.exit_code != 0:
        lines.append(f"[exit code: {output.exit_code}]")

    # Add truncation notice
    if output.truncated:
        lines.append("[output truncated]")

    # Add interrupted notice
    if output.interrupted:
        lines.append("[interrupted]")

    # Add timeout info
    if timeout_ms and output.exit_code == 124:  # 124 is timeout exit code
        lines.append(f"[timed out after {timeout_ms}ms]")

    return '\n'.join(lines)


def render_output_line(
    line: str,
    is_stderr: bool = False,
    timestamp: Optional[str] = None
) -> str:
    """Render a single output line"""
    prefix = "[stderr] " if is_stderr else ""
    ts_prefix = f"[{timestamp}] " if timestamp else ""
    return f"{ts_prefix}{prefix}{line}"