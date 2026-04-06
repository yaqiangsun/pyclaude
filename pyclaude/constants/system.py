# Critical system constants extracted to break circular dependencies
import os

DEFAULT_PREFIX = "You are Claude Code, Anthropic's official CLI for Claude."
AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX = "You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK."
AGENT_SDK_PREFIX = "You are a Claude agent, built on Anthropic's Claude Agent SDK."

CLI_SYSPROMPT_PREFIX_VALUES = [
    DEFAULT_PREFIX,
    AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX,
    AGENT_SDK_PREFIX,
]

CLI_SYSPROMPT_PREFIXES = set(CLI_SYSPROMPT_PREFIX_VALUES)


def get_cli_sysprompt_prefix(
    is_non_interactive: bool = False,
    has_append_system_prompt: bool = False,
    api_provider: str = None,
) -> str:
    """
    Get the appropriate CLI system prompt prefix based on context.

    Args:
        is_non_interactive: Whether running in non-interactive mode
        has_append_system_prompt: Whether there's an appended system prompt
        api_provider: The API provider being used (e.g., 'vertex')

    Returns:
        The appropriate sysprompt prefix string
    """
    if api_provider == 'vertex':
        return DEFAULT_PREFIX

    if is_non_interactive:
        if has_append_system_prompt:
            return AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX
        return AGENT_SDK_PREFIX
    return DEFAULT_PREFIX


def is_attribution_header_enabled() -> bool:
    """
    Check if attribution header is enabled.
    Enabled by default, can be disabled via env var.
    """
    if os.environ.get('CLAUDE_CODE_ATTRIBUTION_HEADER') in ('false', '0', ''):
        return False
    return True


def get_attribution_header(version: str, fingerprint: str, entrypoint: str = None, workload: str = None) -> str:
    """
    Get attribution header for API requests.
    Returns a header string with cc_version (including fingerprint) and cc_entrypoint.

    Args:
        version: The version string
        fingerprint: The client fingerprint
        entrypoint: The entry point (defaults to 'unknown')
        workload: Optional workload identifier

    Returns:
        The attribution header string, or empty string if disabled
    """
    if not is_attribution_header_enabled():
        return ''

    version_str = f"{version}.{fingerprint}"
    entrypoint_str = entrypoint or os.environ.get('CLAUDE_CODE_ENTRYPOINT', 'unknown')

    header = f"x-anthropic-billing-header: cc_version={version_str}; cc_entrypoint={entrypoint_str}"

    if workload:
        header += f"; cc_workload={workload}"

    return header