import click

from click import echo

from .constants import WELCOME_TEXT


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Main function for the daemon. Checks if there is no subcommand
    in the current context and echo the welcome text if not.
    """
    if not ctx.invoked_subcommand:
        echo(WELCOME_TEXT)
