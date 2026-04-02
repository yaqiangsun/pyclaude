"""
Argument substitution utilities.

Utility for substituting $ARGUMENTS placeholders in skill/command prompts.

Supports:
- $ARGUMENTS - replaced with the full arguments string
- $ARGUMENTS[0], $ARGUMENTS[1], etc. - replaced with individual indexed arguments
- $0, $1, etc. - shorthand for $ARGUMENTS[0], $ARGUMENTS[1]
- Named arguments (e.g., $foo, $bar) - when argument names are defined in frontmatter
"""

import re
from typing import List, Optional, Union


# Placeholder for try_parse_shell_command
def _try_parse_shell_command(args: str, key_func=None) -> dict:
    """Try to parse shell command - placeholder."""
    # Simple fallback: split by whitespace
    return {
        "success": False,
        "tokens": args.split(),
    }


def parse_arguments(args: str) -> List[str]:
    """Parse an arguments string into an array of individual arguments.

    Examples:
    - "foo bar baz" => ["foo", "bar", "baz"]
    - 'foo "hello world" baz' => ["foo", "hello world", "baz"]

    Args:
        args: The arguments string to parse

    Returns:
        List of individual arguments
    """
    if not args or not args.strip():
        return []

    result = _try_parse_shell_command(args, lambda key: f"${key}")
    if not result.get("success", False):
        # Fall back to simple whitespace split
        return [t for t in args.split() if t]

    # Filter to only string tokens
    tokens = result.get("tokens", [])
    return [t for t in tokens if isinstance(t, str)]


def parse_argument_names(
    argument_names: Optional[Union[str, List[str]]],
) -> List[str]:
    """Parse argument names from the frontmatter 'arguments' field.

    Accepts either a space-separated string or an array of strings.

    Args:
        argument_names: Argument names to parse

    Returns:
        List of valid argument names
    """
    if not argument_names:
        return []

    def is_valid_name(name: str) -> bool:
        return (
            isinstance(name, str) and
            name.strip() != "" and
            not re.match(r"^\d+$", name)
        )

    if isinstance(argument_names, list):
        return [n for n in argument_names if is_valid_name(n)]
    if isinstance(argument_names, str):
        return [n for n in argument_names.split() if is_valid_name(n)]
    return []


def generate_progressive_argument_hint(
    arg_names: List[str],
    typed_args: List[str],
) -> Optional[str]:
    """Generate argument hint showing remaining unfilled args.

    Args:
        arg_names: Array of argument names from frontmatter
        typed_args: Arguments the user has typed so far

    Hint string like "[arg2] [arg3]" or None if all filled
    """
    remaining = arg_names[len(typed_args):]
    if not remaining:
        return None
    return " ".join(f"[{name}]" for name in remaining)


def substitute_arguments(
    content: str,
    args: Optional[str],
    append_if_no_placeholder: bool = True,
    argument_names: List[str] = [],
) -> str:
    """Substitute $ARGUMENTS placeholders in content with actual argument values.

    Args:
        content: The content containing placeholders
        args: The raw arguments string (may be None)
        append_if_no_placeholder: If True and no placeholders found, appends "ARGUMENTS: {args}"
        argument_names: Optional array of named arguments that map to indexed positions

    Returns:
        The content with placeholders substituted
    """
    # None means no args provided - return content unchanged
    if args is None:
        return content

    parsed_args = parse_arguments(args)
    original_content = content

    # Replace named arguments (e.g., $foo, $bar)
    for i, name in enumerate(argument_names):
        if not name:
            continue
        pattern = rf"\${name}(?!\[\w])"
        content = re.sub(pattern, parsed_args[i] if i < len(parsed_args) else "", content)

    # Replace indexed arguments ($ARGUMENTS[0], $ARGUMENTS[1], etc.)
    content = re.sub(r"\$ARGUMENTS\[(\d+)\]", lambda m: parsed_args[int(m.group(1))] if int(m.group(1)) < len(parsed_args) else "", content)

    # Replace shorthand indexed arguments ($0, $1, etc.)
    content = re.sub(r"\$(\d+)(?!\w)", lambda m: parsed_args[int(m.group(1))] if int(m.group(1)) < len(parsed_args) else "", content)

    # Replace $ARGUMENTS with the full arguments string
    content = content.replace("$ARGUMENTS", args)

    # If no placeholders found and append_if_no_placeholder, append
    if content == original_content and append_if_no_placeholder and args:
        content = content + f"\n\nARGUMENTS: {args}"

    return content


__all__ = [
    "parse_arguments",
    "parse_argument_names",
    "generate_progressive_argument_hint",
    "substitute_arguments",
]