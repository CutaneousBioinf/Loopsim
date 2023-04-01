import click

from . import common
from .analyze import analyze
from .bulk_analyze import bulk_analyze
from .simulate import simulate
from .validate import validate
from .visualize import visualize


@click.group()
@click.option(
    "--delimiter",
    default="\t",
    type=str,
    help="delimiter for outputted files [default: tab]",
)
def cli(delimiter):
    """
    For more thorough explanation of what every command does, please see the documentation.
    """
    common.delimiter = delimiter


cli.add_command(validate)
cli.add_command(simulate)
cli.add_command(analyze)
cli.add_command(bulk_analyze)
cli.add_command(visualize)
