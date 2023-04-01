"""Plot ratio distribution"""

import click
import pandas as pd
import seaborn as sb
from scipy.stats import norm

from . import common


@click.command()
@click.argument("distribution_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("plot_file", type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True))
@click.option(
    "--other",
    type=float,
    help="if this is passed, a Z-test will be conducted on this value against the mean of the ratio distribution",
)
def visualize(distribution_file, plot_file, other):
    """Get visualization and stats from distribution of ratios

    Must pass distribution of (simulated) data.
    Optionally, can pass a data point for statistical comparison with --other flag
    """

    # Print params
    print(f"Obtaining overlapping ratios from: {distribution_file}.")

    # Get data
    dist = pd.read_table(distribution_file, header=None, delimiter=common.detect_delimiter(distribution_file))

    # Create distribution plot
    sb.set_style("dark")
    ax = sb.histplot(data=dist[0], label="Simulated")
    ax.set(
        title="Frequency of Loop Overlaps with Intervals of Interest",
        xlabel="Proportion of Loops that Overlap with Regions of Interest",
    )

    if other:
        ax.axvline(other, color="orange", label="Experimental")

    legend_handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=legend_handles, title="Legend")
    sb.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

    # Export to jpg
    ax.get_figure().savefig(plot_file, bbox_inches="tight", dpi=300)
    print(f"Exported plot to {plot_file}")

    # Summary stats
    print("Summary stats:")
    print(f"Distribution mean: {dist[0].mean()}")
    print(f"Distribution std: {dist[0].std()}")
    print(f"Distribution min: {dist[0].min()}")
    print(f"Distribution median: {dist[0].median()}")
    print(f"Distribution max: {dist[0].max()}")

    # Statistical test (if comparison value is passed)
    if other:
        print("\nZ-test:")
        z_stat = (other - dist[0].mean()) / dist[0].std()
        print(f"Z-statistic: {z_stat}")
        print(f"p-value: {str(1 - norm.cdf(z_stat))}")
