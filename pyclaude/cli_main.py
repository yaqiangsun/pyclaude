"""CLI entry point for pyclaude."""
import asyncio
import sys
import os
import logging
from typing import Optional
import click
from typing import Any

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_api_key() -> Optional[str]:
    """Get API key from environment or settings."""
    from pyclaude.utils.auth import get_anthropic_api_key
    return get_anthropic_api_key()


@click.command()
@click.argument("prompt", required=False)
@click.option("--model", "-m", default=None, help="Model to use (default: from settings or claude-sonnet-4-20250514)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--max-turns", "-n", type=int, help="Maximum number of turns")
@click.option("--repl", "-i", is_flag=True, help="Start REPL mode")
def main(
    prompt: Optional[str],
    model: Optional[str],
    verbose: bool,
    max_turns: Optional[int],
    repl: bool,
) -> None:
    """Claude Code - AI coding assistant"""
    setup_logging(verbose)

    # Initialize bootstrap first to set up working directory for settings
    from . import bootstrap
    bootstrap.initialize_state(os.getcwd())

    # Get model from settings if not specified via CLI
    if model is None:
        from .utils.model import get_main_loop_model
        model = get_main_loop_model()

    if repl:
        click.echo("Starting REPL mode...")
        # REPL mode - TODO: implement
        _run_repl()
        return

    # If no prompt provided, start REPL mode by default
    if not prompt:
        click.echo("Starting REPL mode (no prompt provided)...")
        _run_repl()
        return

    # Run single query
    try:
        asyncio.run(_run_query(prompt, model=model, verbose=verbose, max_turns=max_turns))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            logger.exception("Error running query")
        sys.exit(1)


async def _run_query(
    prompt: str,
    model: str = "claude-sonnet-4-20250514",
    verbose: bool = False,
    max_turns: Optional[int] = None,
) -> None:
    """Run a query using the Claude API."""
    from . import bootstrap
    from .query_engine import QueryEngine, QueryEngineConfig
    from .tool import Tool
    from .tools import get_all_tools
    from .commands import get_all_commands
    from .state import AppState, get_app_state, set_app_state

    # Initialize state
    cwd = os.getcwd()
    bootstrap.initialize_state(cwd)

    # Get API key
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

    # Load tools and commands
    tools = get_all_tools()
    commands = get_all_commands()

    click.echo(f"Using model: {model}")
    click.echo(f"Prompt: {prompt}")
    click.echo(f"Loaded {len(tools)} tools, {len(commands)} commands")

    # Create query engine config
    async def default_can_use_tool(
        tool: Tool,
        input_dict: dict,
        context: Any,
        assistant_message: dict,
        tool_use_id: str,
        force_decision: Optional[str] = None,
    ) -> dict:
        return {"behavior": "allow", "updated_input": input_dict}

    config = QueryEngineConfig(
        cwd=cwd,
        tools=tools,
        commands=commands,
        mcp_clients=[],
        agents=[],
        can_use_tool=default_can_use_tool,
        get_app_state=get_app_state,
        set_app_state=set_app_state,
        read_file_cache={},
        user_specified_model=model,
        verbose=verbose,
        max_turns=max_turns,
    )

    # Create and run query engine
    engine = QueryEngine(config)

    # Execute the query and collect results
    has_output = False
    tool_call_count = 0

    async for message in engine.submit_message(prompt):
        msg_type = message.get('type')

        if msg_type == 'tool_call':
            # Output tool call - show tool name and input
            tool_name = message.get('tool_name', '')
            tool_input = message.get('tool_input', {})
            tool_call_count += 1

            # Format input for display
            input_str = _format_tool_input(tool_name, tool_input)
            click.echo(f"[{tool_call_count}] → {tool_name}: {input_str}")
            has_output = True

        elif msg_type == 'message':
            content = message.get('message', {}).get('content', [])
            for block in content:
                if block.get('type') == 'text':
                    text = block.get('text', '')
                    # Remove excessive empty lines
                    text = '\n'.join(line for line in text.split('\n') if line.strip())
                    if text.strip():
                        click.echo(text)
                        has_output = True
                # Skip thinking output in normal mode (only show in verbose)

        elif msg_type == 'tool_result':
            # Output action step - show tool execution result
            result = message.get('result', {})
            tool_id = result.get('tool_use_id', '')
            content = result.get('content', '')
            is_error = result.get('is_error', False)

            # Show truncated content for action feedback
            if content:
                display_content = content[:150].replace('\n', ' ') + ('...' if len(content) > 150 else '')
            else:
                display_content = '(empty)'

            if is_error:
                click.echo(f"[{tool_call_count}] ✗ Error: {display_content}")
            else:
                click.echo(f"[{tool_call_count}] ✓ {display_content}")
            has_output = True

        elif msg_type == 'error':
            click.echo(f"Error: {message.get('error')}", err=True)
            has_output = True


def _format_tool_input(tool_name: str, tool_input: dict) -> str:
    """Format tool input for display."""
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        return f"`{command[:80]}{'...' if len(command) > 80 else ''}`"
    elif tool_name == 'Read':
        path = tool_input.get('file_path', '')
        offset = tool_input.get('offset')
        limit = tool_input.get('limit')
        parts = [path]
        if offset is not None:
            parts.append(f"offset={offset}")
        if limit is not None:
            parts.append(f"limit={limit}")
        return " ".join(parts)
    elif tool_name == 'Glob':
        pattern = tool_input.get('pattern', '')
        path = tool_input.get('path', '')
        if path:
            return f'pattern="{pattern}" path="{path}"'
        return f'pattern="{pattern}"'
    else:
        # Generic display
        items = [f"{k}={v}" for k, v in tool_input.items() if k not in ('description', 'timeout')]
        return ", ".join(items[:3]) + ("..." if len(items) > 3 else "")

    click.echo("")


async def run_command_async(cmd_func, args, context):
    """Run a command function in a new event loop."""
    import asyncio
    try:
        # Try to get current loop
        loop = asyncio.get_running_loop()
        # We're in an async context, create a task
        return await cmd_func(args, context)
    except RuntimeError:
        # No running loop, we can use asyncio.run
        return asyncio.run(cmd_func(args, context))


def get_recent_activity() -> list:
    """Get recent activity from sessions."""
    try:
        from .utils.list_sessions_impl import list_sessions_impl
        sessions = list_sessions_impl()
        # Return most recent sessions (up to 3)
        return sessions[:3] if sessions else []
    except Exception:
        return []


def get_tips_for_getting_started() -> list:
    """Get tips based on current project state."""
    tips = []
    import os
    from pathlib import Path

    cwd = Path(os.getcwd())

    # Check for CLAUDE.md
    claude_md = cwd / 'CLAUDE.md'
    if not claude_md.exists():
        tips.append("Run /init to create a CLAUDE.md file with instructions for Claude")
    else:
        tips.append(f"CLAUDE.md found in {cwd.name}")

    # Check for .git
    git_dir = cwd / '.git'
    if git_dir.exists():
        tips.append("Git repository detected")

    # Check for package.json or other project files
    project_files = ['package.json', 'Cargo.toml', 'pyproject.toml', 'requirements.txt']
    for pf in project_files:
        if (cwd / pf).exists():
            tips.append(f"{pf} detected - this appears to be a project")
            break

    if not tips:
        tips.append("Type /help for available commands")

    return tips[:3]  # Return up to 3 tips


def show_welcome_banner() -> None:
    """Show welcome banner similar to src Claude Code."""
    # Get version
    from .constants.product import get_product_version, get_product_name
    version = get_product_version()
    product = get_product_name()

    # Get dynamic content
    recent_activity = get_recent_activity()
    tips = get_tips_for_getting_started()

    # Format tips for display
    tips_lines = []
    if tips:
        tips_lines.append(tips[0] if len(tips) > 0 else "")
        tips_lines.append("─" * 62 if len(tips) > 1 else "")
        tips_lines.append(tips[1] if len(tips) > 1 else "")
        tips_lines.append(tips[2] if len(tips) > 2 else "")
    else:
        tips_lines = ["", "─" * 62, "", ""]

    # Format recent activity with relative time
    activity_lines = []
    if recent_activity:
        for activity in recent_activity[:3]:
            title = activity.get('customTitle') or activity.get('firstPrompt') or 'Untitled'
            title = title[:40] if title else 'Untitled'

            # Format time as relative (e.g., "2h ago", "3d ago")
            mod_time = activity.get('modified', '')
            if mod_time:
                try:
                    import time as time_module
                    mod_timestamp = float(mod_time)
                    now = time_module.time()
                    diff = now - mod_timestamp

                    if diff < 60:
                        time_str = "just now"
                    elif diff < 3600:
                        time_str = f"{int(diff/60)}m ago"
                    elif diff < 86400:
                        time_str = f"{int(diff/3600)}h ago"
                    elif diff < 604800:
                        time_str = f"{int(diff/86400)}d ago"
                    else:
                        time_str = f"{int(diff/604800)}w ago"
                except Exception:
                    time_str = ""
            else:
                time_str = ""

            activity_lines.append(f"{title:<40} {time_str}")
    else:
        activity_lines = ["No recent activity", "", ""]

    # Get model and working directory
    import os
    model = os.environ.get('CLAUDE_MODEL', 'MiniMaxAI/MiniMax-M2.5 with h…')
    cwd = os.getcwd()
    cwd_short = cwd if len(cwd) <= 40 else '~' + cwd[-39:]

    # Fixed width: 122 chars per line (52 + 67 + 3 for │ chars)
    W = 122
    # DIV is where the first │ appears (52 chars of content on left)
    DIV = 52

    # Left side width = DIV (52 chars), right side = W - DIV - 1 (67 chars)
    LEFT_W = DIV
    RIGHT_W = W - DIV - 1

    # Simple pad using character count
    def pad(s: str, w: int) -> str:
        return s[:w] + ' ' * max(0, w - len(s)) if s else ' ' * w

    def make_line(left: str, right: str = "") -> str:
        """Make a full line with left and right content."""
        left_padded = pad(left, LEFT_W)
        right_padded = pad(right, RIGHT_W)
        return f"│{left_padded}│{right_padded}│"

    # Welcome banner
    title = f"╭─── {product} {version} "
    click.echo(title + "─" * (W - len(title) - 1) + "╮")
    click.echo(make_line("", "Tips for getting started"))
    click.echo(make_line("     Welcome back!", tips_lines[0] if tips_lines else ""))
    click.echo(make_line("", tips_lines[1] if len(tips_lines) > 1 else ""))
    click.echo(make_line("  ▐▛███▜▌", tips_lines[2] if len(tips_lines) > 2 else ""))
    click.echo(make_line(" ▝▜█████▛▘", ""))
    click.echo(make_line("   ▘▘ ▝▝", "Recent activity"))
    click.echo(make_line("", activity_lines[0] if activity_lines else ""))
    click.echo(make_line("", activity_lines[1] if len(activity_lines) > 1 else ""))
    click.echo(make_line("", activity_lines[2] if len(activity_lines) > 2 else ""))
    click.echo(make_line("", ""))
    click.echo(make_line(f" {model[:LEFT_W-3]}", "/resume for more"))
    click.echo(make_line(f"            {cwd_short}", ""))
    click.echo("╰" + "─" * (W - 2) + "╯")


def show_command_suggestions(partial: str) -> None:
    """Show command suggestions for partial command."""
    from .commands import COMMANDS, get_command_description

    matches = []
    # Check exact match and prefix match (e.g., plugin -> plugins)
    for name, info in COMMANDS.items():
        if name.startswith(partial.lower()) or partial.lower().startswith(name):
            matches.append((name, get_command_description(name)))

    # Also check if partial matches any alias
    if not matches:
        for name, info in COMMANDS.items():
            for alias in info.get('aliases', []):
                if alias.startswith(partial.lower()):
                    matches.append((name, get_command_description(name)))
                    break

    if matches:
        click.echo(f"Unknown command: /{partial}")
        click.echo("")
        click.echo("Available commands:")
        # Remove duplicates while preserving order
        seen = set()
        for name, desc in matches:
            if name not in seen:
                seen.add(name)
                click.echo(f"  /{name:<15} {desc}")
    else:
        # Show all commands that start with the same letter
        letter = partial[0].lower() if partial else ''
        if letter:
            click.echo(f"Commands starting with /{letter}:")
            for name, info in sorted(COMMANDS.items()):
                if name.startswith(letter):
                    click.echo(f"  /{name:<15} {get_command_description(name)}")
        else:
            # Show all available commands
            click.echo("Available commands:")
            for name, info in sorted(COMMANDS.items()):
                click.echo(f"  /{name:<15} {get_command_description(name)}")


def _run_repl() -> None:
    """Run interactive REPL mode."""
    import asyncio

    async def run_repl_async() -> None:
        from . import bootstrap
        from .query_engine import QueryEngine, QueryEngineConfig
        from .tool import Tool
        from .tools import get_all_tools
        from .commands import get_all_commands
        from .state import get_app_state, set_app_state

        # Initialize
        cwd = os.getcwd()
        bootstrap.initialize_state(cwd)

        # Get API key
        api_key = get_api_key()
        if not api_key:
            click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
            return

        # Load tools and commands
        tools = get_all_tools()
        commands = get_all_commands()

        # Show welcome banner similar to src
        show_welcome_banner()

        click.echo("")

        # Create query engine config
        async def default_can_use_tool(
            tool: Tool,
            input_dict: dict,
            context: Any,
            assistant_message: dict,
            tool_use_id: str,
            force_decision: Optional[str] = None,
        ) -> dict:
            return {"behavior": "allow", "updated_input": input_dict}

        # Get model
        from .utils.model import get_main_loop_model
        model = get_main_loop_model()

        config = QueryEngineConfig(
            cwd=cwd,
            tools=tools,
            commands=commands,
            mcp_clients=[],
            agents=[],
            can_use_tool=default_can_use_tool,
            get_app_state=get_app_state,
            set_app_state=set_app_state,
            read_file_cache={},
            user_specified_model=model,
        )

        # Create engine - this persists across turns
        engine = QueryEngine(config)

        # Run REPL loop
        while True:
            try:
                prompt = input("❯ ")

                # Check for slash commands first
                if prompt.strip().startswith('/'):
                    from .utils.slash_command_parsing import parse_slash_command
                    from .commands import COMMANDS

                    parsed = parse_slash_command(prompt)
                    if parsed:
                        cmd_name, cmd_args = parsed
                        # Find command (check aliases too)
                        cmd_info = None
                        for name, info in COMMANDS.items():
                            if name == cmd_name or cmd_name in info.get('aliases', []):
                                cmd_info = info
                                cmd_name = name
                                break

                        if cmd_info and cmd_info.get('call'):
                            try:
                                # Use a new event loop for the command
                                result = await run_command_async(cmd_info['call'], cmd_args, {})
                                if result:
                                    result_type = result.get('type')
                                    if result_type == 'text':
                                        click.echo(result.get('value', ''))
                                    elif result_type == 'exit':
                                        # Don't print here - the loop exit handles it
                                        # The final "Goodbye!" is printed after the loop
                                        pass
                                    elif result_type == 'skip':
                                        pass  # Don't display anything
                                    else:
                                        click.echo(str(result))
                                # Check if result indicates exit - just break, don't print
                                if result and (result.get('exit') or result.get('type') == 'exit'):
                                    break
                            except Exception as e:
                                click.echo(f"Error executing /{cmd_name}: {e}", err=True)
                        else:
                            # Show command suggestions
                            show_command_suggestions(cmd_name)
                        click.echo("")
                        continue

                # Handle plain exit/quit
                if prompt.lower().strip() in ('exit', 'quit', 'q'):
                    break

                if not prompt.strip():
                    continue

                # Run query and display results
                tool_call_count = 0

                async for message in engine.submit_message(prompt):
                    msg_type = message.get('type')

                    if msg_type == 'tool_call':
                        tool_name = message.get('tool_name', '')
                        tool_input = message.get('tool_input', {})
                        tool_call_count += 1
                        input_str = _format_tool_input(tool_name, tool_input)
                        click.echo(f"[{tool_call_count}] → {tool_name}: {input_str}")

                    elif msg_type == 'message':
                        content = message.get('message', {}).get('content', [])
                        for block in content:
                            if block.get('type') == 'text':
                                text = block.get('text', '')
                                text = '\n'.join(line for line in text.split('\n') if line.strip())
                                if text.strip():
                                    click.echo(text)

                    elif msg_type == 'tool_result':
                        result = message.get('result', {})
                        content = result.get('content', '')
                        is_error = result.get('is_error', False)
                        if content:
                            display_content = content[:150].replace('\n', ' ') + ('...' if len(content) > 150 else '')
                        else:
                            display_content = '(empty)'
                        if is_error:
                            click.echo(f"[{tool_call_count}] ✗ Error: {display_content}")
                        else:
                            click.echo(f"[{tool_call_count}] ✓ {display_content}")

                    elif msg_type == 'auto_compact':
                        pre = message.get('pre_compact_token_count', 0)
                        post = message.get('post_compact_token_count', 0)
                        click.echo(f"[Auto-compact] {pre} → {post} tokens")

                    elif msg_type == 'error':
                        click.echo(f"Error: {message.get('error')}", err=True)

                click.echo("")

            except KeyboardInterrupt:
                click.echo("")
                break
            except EOFError:
                break

        click.echo("Goodbye!")

    asyncio.run(run_repl_async())


if __name__ == "__main__":
    main()