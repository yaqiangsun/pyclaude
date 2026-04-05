"""Agents command - manage AI agents."""
import click


@click.command()
@click.argument('action', required=False, default='list')
@click.option('--name', help='Agent name')
def agents(action: str = 'list', name: str = None):
    """Manage AI agents.

    Actions: list, create, delete, start, stop
    """
    if action == 'list':
        click.echo("Available agents:")
    elif action == 'create' and name:
        click.echo(f"Creating agent: {name}")
    else:
        click.echo("Usage: /agents [list|create|delete|start|stop] [--name NAME]")


__all__ = ['agents']