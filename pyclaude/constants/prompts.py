"""Prompt templates and constants."""

from typing import Dict, List


# System prompt templates
DEFAULT_SYSTEM_PROMPT = """You are Claude Code, an AI programming assistant.

You are helpful, concise, and focused on writing code.

When writing code:
- Follow the existing code style and conventions
- Write clean, readable code with appropriate comments
- Consider edge cases and error handling

When explaining:
- Be concise and practical
- Focus on the solution, not the problem
- Provide code examples when helpful
"""

# Prompt boundaries
SYSTEM_PROMPT_DYNAMIC_BOUNDARY = "<<<SYS_PROMPT_END>>>"
SYSTEM_PROMPT_START = "<<SYS_PROMPT_START>>"
SYSTEM_PROMPT_END = "<<SYS_PROMPT_END>>"

# CLI prompt prefixes
CLI_SYSPROMPT_PREFIXES: Dict[str, str] = {
    'default': DEFAULT_SYSTEM_PROMPT,
    'code': 'You are a code-focused assistant.',
    'review': 'You are a code review assistant.',
    'debug': 'You are a debugging assistant.',
}

# Context limits
MAX_CONTEXT_TOKENS = 200000
MAX_INPUT_TOKENS = 180000
MAX_OUTPUT_TOKENS = 8192

# Prompt sections
PROMPT_SECTION_SYSTEM = 'system'
PROMPT_SECTION_TOOLS = 'tools'
PROMPT_SECTION_CONTEXT = 'context'
PROMPT_SECTION_CONVERSATION = 'conversation'


def get_system_prompt(prompt_type: str = 'default') -> str:
    """Get system prompt by type."""
    return CLI_SYSPROMPT_PREFIXES.get(prompt_type, DEFAULT_SYSTEM_PROMPT)


def get_prompt_sections() -> List[str]:
    """Get all prompt sections."""
    return [
        PROMPT_SECTION_SYSTEM,
        PROMPT_SECTION_TOOLS,
        PROMPT_SECTION_CONTEXT,
        PROMPT_SECTION_CONVERSATION,
    ]


__all__ = [
    'DEFAULT_SYSTEM_PROMPT',
    'SYSTEM_PROMPT_DYNAMIC_BOUNDARY',
    'SYSTEM_PROMPT_START',
    'SYSTEM_PROMPT_END',
    'CLI_SYSPROMPT_PREFIXES',
    'MAX_CONTEXT_TOKENS',
    'MAX_INPUT_TOKENS',
    'MAX_OUTPUT_TOKENS',
    'PROMPT_SECTION_SYSTEM',
    'PROMPT_SECTION_TOOLS',
    'PROMPT_SECTION_CONTEXT',
    'PROMPT_SECTION_CONVERSATION',
    'get_system_prompt',
    'get_prompt_sections',
]