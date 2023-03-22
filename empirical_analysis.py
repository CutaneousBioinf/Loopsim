#!/usr/bin/env python3
"""Script to do Hi-C loop analysis and empirical distribution"""
# Invariant: we are assuming that the loop files passed in are all valid

import os

import click
import numpy as np
import pandas as pd
from detect_delimiter import detect

# from multiprocesspandas import applyparallel


def main(sims_dir, intervals_file):
    intervals = pd.read_table(intervals_file, header=None, delimiter=detect_delimiter(intervals_file))
    ratios = []

    for filename in os.listdir(sims_dir):
        sim_file = os.path.join(sims_dir, filename)
        analyze_loop_file(sim_file, intervals, ratios)

    pd.Series(ratios).to_csv("ratio_dist", header=None, index=None)


def analyze_loop_file(loop_in_file, intervals, ratios):
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=detect_delimiter(loop_in_file))
    loop_in[0] = loop_in[0].astype("unicode")
    intervals[0] = intervals[0].astype("unicode")

    loop_in_original_len = len(loop_in)
    loop_in[6] = loop_in.apply(is_overlapping_hic, axis=1, args=(intervals,))
    loop_in = loop_in.loc[loop_in[6].notnull()]
    # loop_in.to_csv("analysis", header=None, index=None)
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


def detect_delimiter(filename):
    with open(filename) as f:
        firstline = f.readline()
        return detect(firstline)


if __name__ == "__main__":
    main("out", "95_BCS_psor_loci")
