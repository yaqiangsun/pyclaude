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
    """Get API key from environment."""
    return os.environ.get('ANTHROPIC_API_KEY')


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

    if not prompt:
        click.echo("Error: Prompt required", err=True)
        sys.exit(1)

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


def _run_repl() -> None:
    """Run interactive REPL mode."""
    from . import bootstrap
    bootstrap.initialize_state(os.getcwd())

    click.echo("PyClaude REPL")
    click.echo("Type 'exit' to quit")
    click.echo("")

    while True:
        try:
            prompt = input("> ")
            if prompt.lower() in ('exit', 'quit', 'q'):
                break
            if prompt.strip():
                click.echo(f"Processing: {prompt}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

    click.echo("Goodbye!")


if __name__ == "__main__":
    main()