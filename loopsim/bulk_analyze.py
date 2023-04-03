"""BULK loop analysis and empirical distribution"""
# Invariant: we are assuming that the loop files passed in are all valid

import os

import click
import pandas as pd

from . import common
from .analyze import analyze_loop_file


@click.command()
@click.argument("loop_in_directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument("intervals_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument(
    "overlapping_ratio_distribution_file", type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True)
)
@click.option(
    "--loop-out-directory",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    help="if passed, will output summary table for each file in LOOP_IN_DIRECTORY to specified directory (omit for speed)",
)
def bulk_analyze(loop_in_directory, intervals_file, overlapping_ratio_distribution_file, loop_out_directory):
    """Perform analysis on a distribution of loop files

    If --loop-out-directory is not passed, this command will be like running 'analyze' on every file in LOOP_IN_DIRECTORY (i.e it will not save the summary file for each file in LOOP_IN_DIRECTORY)

    NOTE: any data in --loop_out_directory may be overwritten!!

    NOTE: OVERLAPPING_RATIO_DISTRIBUTION_FILE will only contain nonzero ratios (i.e. loops that have >=1 overlap with an interval of interest)
    """

    # Print params
    print(f"Input loop files directory: {loop_in_directory}")
    print(f"Intervals file: {intervals_file}")
    print(f"Ratio distribution file: {overlapping_ratio_distribution_file}")
    print(f"Delimiter for output: '{common.delimiter}'")
    if loop_out_directory:
        print(f"Output loop files directory: {loop_out_directory}")

    # Get data dir sorted out
    if loop_out_directory and not os.path.isdir(loop_out_directory):
        print("Output directory does not exist.")
        os.makedirs(loop_out_directory)
        print("Output directory created!")

    # Get intervals
    intervals = pd.read_table(intervals_file, header=None, delimiter=common.detect_delimiter(intervals_file))

    # Do analysis for all input loop files
    ratios = []
    # this if/else with repeated code is ugly as hell but probably worth the optimization (though with python idk ;) )
    if loop_out_directory:
        for i, filename in enumerate(os.listdir(loop_in_directory)):
            sim_file = os.path.join(loop_in_directory, filename)
            loop_out = analyze_loop_file(sim_file, intervals, ratios)
            output_filepath = f"{loop_out_directory}/summary_table_{i}.loop"
            loop_out.to_csv(output_filepath, header=None, index=None, sep=common.delimiter)
        print(f"Finished outputting analyzed files to {loop_out_directory}")
    else:
        for filename in os.listdir(loop_in_directory):
            sim_file = os.path.join(loop_in_directory, filename)
            analyze_loop_file(sim_file, intervals, ratios)

    # Output ratios
    pd.Series(ratios).to_csv(overlapping_ratio_distribution_file, header=None, index=None, sep=common.delimiter)
    print(f"Finished outputting ratio distribution to {overlapping_ratio_distribution_file}")
