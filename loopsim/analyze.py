"""loop analysis and empirical distribution"""
# Invariant: we are assuming that the loop files passed in are all valid


import click
import numpy as np
import pandas as pd

from . import common


@click.command()
@click.argument("loop_in_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("loop_out_file", type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True))
@click.argument("intervals_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
def analyze(loop_in_file, loop_out_file, intervals_file):
    """Perform analysis on a single loop file

    Output the inputted loop file with an extra column.
    Each row of the extra column will have the indices in the reference file that the loop on that row overlaps with."""

    # Print params
    print(f"Input loop file: {loop_in_file}")
    print(f"Output loop file: {loop_out_file}")
    print(f"Intervals file: {intervals_file}")
    print(f"Delimiter for output: '{common.delimiter}'")

    # Get intervals
    intervals = pd.read_table(intervals_file, header=None, delimiter=common.detect_delimiter(intervals_file))

    # Do analysis
    ratios = []
    loop_out = analyze_loop_file(loop_in_file, intervals, ratios)

    # Output analysis
    loop_out.to_csv(loop_out_file, header=None, index=None, sep=common.delimiter)
    print(f"Outputted analyzed loop file to {loop_out_file}")
    print(f"Ratio of overlapping intervals out of the total number of loops was: {ratios[0]}")


def analyze_loop_file(loop_in_file, intervals, ratios):
    """ratios isn't used here but is used for bulk analysis"""
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=common.detect_delimiter(loop_in_file))

    loop_in[0] = loop_in[0].astype("unicode")
    intervals[0] = intervals[0].astype("unicode")

    loop_in[6] = loop_in.apply(is_overlapping_hic, axis=1, args=(intervals,))

    ratios.append(len(loop_in.loc[loop_in[6].notnull()]) / len(loop_in))

    return loop_in


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
