"""Branch command - manage git branches."""
import click


@click.command()
@click.argument('action', required=False)
@click.option('-a', '--all', is_flag=True, help='Show all branches')
def branch(action: str = None, all: bool = False):
    """Manage git branches."""
    if action == 'list' or action is None:
        click.echo("Git branches:")
    else:
        click.echo(f"Branch: {action}")


__all__ = ['branch']