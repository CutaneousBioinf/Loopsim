import click

# from loopsim.visualize import visualize
from . import common
from .analyze import analyze
from .simulate import simulate
from .validate import validate


@click.group()
@click.option(
    "--delimiter",
    default="\t",
    type=str,
    help="delimiter for outputted files [default: tab]",
)
def cli(delimiter):
    common.delimiter = delimiter


cli.add_command(validate)
cli.add_command(simulate)
cli.add_command(analyze)
# main.add_command(visualize)
