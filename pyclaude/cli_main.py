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


def show_welcome_banner() -> None:
    """Show welcome banner similar to src Claude Code."""
    # Get version
    from .constants.product import get_product_version, get_product_name
    version = get_product_version()
    product = get_product_name()

    # Welcome banner with ASCII art
    click.echo(f"╭─── {product} {version} ──────────────────────────────────────────────────────────────────────────────────────────╮")
    click.echo(f"│                                                    │ Tips for getting started                                    │")
    click.echo(f"│                    Welcome back!                   │ Run /init to create a CLAUDE.md file with instructions for… │")
    click.echo(f"│                                                    │ ─────────────────────────────────────────────────────────── │")
    click.echo(f"│                       ▐▛███▜▌                      │ Recent activity                                             │")
    click.echo(f"│                      ▝▜█████▛▘                     │ No recent activity                                          │")
    click.echo(f"│                        ▘▘ ▝▝                       │                                                             │")
    click.echo(f"│                                                    │                                                             │")
    click.echo(f" MiniMaxAI/MiniMax-M2.5 with h… · API Usage Billing │                                                             │")
    import os
    click.echo(f"            {os.getcwd()}             │                                                             │")
    click.echo("╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯")


def show_command_suggestions(partial: str) -> None:
    """Show command suggestions for partial command."""
    from .commands import COMMANDS

    matches = []
    # Check exact match and prefix match (e.g., plugin -> plugins)
    for name, info in COMMANDS.items():
        if name.startswith(partial.lower()) or partial.lower().startswith(name):
            matches.append((name, info.get('description', '')))

    # Also check if partial matches any alias
    if not matches:
        for name, info in COMMANDS.items():
            for alias in info.get('aliases', []):
                if alias.startswith(partial.lower()):
                    matches.append((name, info.get('description', '')))
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
                    click.echo(f"  /{name:<15} {info.get('description', '')}")
        else:
            # Show all available commands
            click.echo("Available commands:")
            for name, info in sorted(COMMANDS.items()):
                click.echo(f"  /{name:<15} {info.get('description', '')}")


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