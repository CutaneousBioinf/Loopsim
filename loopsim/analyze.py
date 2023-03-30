"""loop analysis and empirical distribution"""
# Invariant: we are assuming that the loop files passed in are all valid

import os

import click
import numpy as np
import pandas as pd

from . import common


@click.command()
@click.argument("intervals_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("simulation_data_directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument("ratio_distribution_file", type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True))
def analyze(intervals_file, simulation_data_directory, ratio_distribution_file):
    """Perform analysis on the distribution of simulated files.

    Return a file with a distribution of the ratio of loops in each simulation that overlap with regions of interest"""

    # Get intervals
    intervals = pd.read_table(intervals_file, header=None, delimiter=common.detect_delimiter(intervals_file))

    # Do analysis
    ratios = []
    for filename in os.listdir(simulation_data_directory):
        sim = os.path.join(simulation_data_directory, filename)
        analyze_loop_file(sim, intervals, ratios)

    # Output
    pd.Series(ratios).to_csv(ratio_distribution_file, header=None, index=None, sep=common.delimiter)


def analyze_loop_file(loop_in_file, intervals, ratios):
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=common.detect_delimiter(loop_in_file))
    loop_in[0] = loop_in[0].astype("unicode")
    intervals[0] = intervals[0].astype("unicode")

    loop_in_original_len = len(loop_in)
    loop_in[6] = loop_in.apply(is_overlapping_hic, axis=1, args=(intervals,))
    loop_in = loop_in.loc[loop_in[6].notnull()]
    ratios.append(len(loop_in) / loop_in_original_len)


def ranges_overlap(x_start, x_end, y_start, y_end):
    """do ranges overlap? (boundaries being the same counts as overlapping)"""
    return x_start <= y_end and y_start <= x_end


def is_overlapping_hic(loop, intervals):
    """check if loop has overlaps with an interval of interest (return indices)"""
    intervals_chr = intervals.loc[intervals[0] == loop[0]]
    loop_start = loop[1]
    loop_end = loop[5]
    overlaps = intervals_chr.apply(
        lambda row, start, end: ranges_overlap(row[1], row[2], start, end), args=(loop_start, loop_end), axis=1
    )
    if len(overlaps[overlaps].index.values):
        return overlaps[overlaps].index.values
    return np.NaN
