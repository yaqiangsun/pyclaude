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
@click.option("--model", "-m", default="claude-sonnet-4-20250514", help="Model to use")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--max-turns", "-n", type=int, help="Maximum number of turns")
@click.option("--repl", "-i", is_flag=True, help="Start REPL mode")
def main(
    prompt: Optional[str],
    model: str,
    verbose: bool,
    max_turns: Optional[int],
    repl: bool,
) -> None:
    """Claude Code - AI coding assistant"""
    setup_logging(verbose)

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
    from .utils import get_main_loop_model

    # Initialize state
    cwd = os.getcwd()
    bootstrap.initialize_state(cwd)

    # Get API key
    api_key = get_api_key()
    if not api_key:
        click.echo("Error: ANTHROPIC_API_KEY not set", err=True)
        sys.exit(1)

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
        tools=[],  # TODO: add tools
        commands=[],
        mcp_clients=[],
        agents=[],
        can_use_tool=default_can_use_tool,
        get_app_state=lambda: {},
        set_app_state=lambda f: None,
        read_file_cache={},
        user_specified_model=model,
        verbose=verbose,
        max_turns=max_turns,
    )

    # Create and run query engine
    engine = QueryEngine(config)

    click.echo(f"Using model: {model}")
    click.echo(f"Prompt: {prompt}")
    click.echo("Query engine initialized (full execution not yet implemented)")


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