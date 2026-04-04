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
    click.echo("\n--- Response ---")

    async for message in engine.submit_message(prompt):
        msg_type = message.get('type')

        if msg_type == 'message':
            content = message.get('message', {}).get('content', [])
            for block in content:
                if block.get('type') == 'text':
                    click.echo(block.get('text', ''))
                elif block.get('type') == 'thinking':
                    if verbose:
                        click.echo(f"[Thinking] {block.get('thinking', '')[:100]}...")

        elif msg_type == 'tool_result':
            result = message.get('result', {})
            tool_id = result.get('tool_use_id', '')
            content = result.get('content', '')
            is_error = result.get('is_error', False)
            if verbose:
                prefix = "[Error] " if is_error else "[Tool Result] "
                click.echo(f"{prefix}{content[:200]}...")

        elif msg_type == 'error':
            click.echo(f"Error: {message.get('error')}", err=True)

    click.echo("\n--- Done ---")


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