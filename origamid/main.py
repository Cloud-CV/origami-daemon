import click
import logging

from .constants import WELCOME_TEXT
from .api import run_server
from .logger import OrigamiLogger

logger = OrigamiLogger(
    file_log_level=logging.DEBUG, console_log_level=logging.DEBUG)


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Origami daemon is an application which deploys and manages demos on
    CloudCV servers.
    """
    if not ctx.invoked_subcommand:
        click.echo(WELCOME_TEXT)


main.add_command(run_server)
