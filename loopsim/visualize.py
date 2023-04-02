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
    ax = sb.histplot(data=dist[0], label="Simulated", kde=True)
    ax.set(
        title=f"Distribution of Overlapping Ratios by Frequency (N = {len(dist)})", xlabel="Overlapping Ratio", ylabel="Frequency"
    )

    if other:
        ax.axvline(other, color="orange", label="Experimental")

    legend_handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=legend_handles)
    sb.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

    # Export to jpg
    ax.get_figure().savefig(plot_file, bbox_inches="tight", dpi=300)
    print(f"Exported plot to {plot_file}")

    # Summary stats
    print("\nSummary stats:")
    print(f"Distribution mean: {dist[0].mean()}")
    print(f"Distribution std: {dist[0].std()}")
    print(f"Distribution min: {dist[0].min()}")
    print(f"Distribution median: {dist[0].median()}")
    print(f"Distribution max: {dist[0].max()}")

    # Statistical tests (if comparison value is passed)
    if other:
        print("\nCalculating p-value based on empirical distribution:")
        num_larger = len(dist.loc[dist[0] > other])
        print(f"p-value: {num_larger / len(dist):.20f}")

        print("\nCalculating p-value based on normal distribution:")
        z_stat = (other - dist[0].mean()) / dist[0].std()
        print(f"p-value: {1 - norm.cdf(z_stat):.20f}")
