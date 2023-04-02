"""Validate loop file used as input"""

import click
import numpy as np
import pandas as pd

from . import common


@click.command()
@click.argument("loop_in_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("loop_out_file", type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True))
@click.argument("chromosome_region_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option(
    "--flag-end-size",
    show_default=True,
    default=100_000,
    type=int,
    help="warn on loop ends that are sized >= this param",
)
def validate(loop_in_file, loop_out_file, chromosome_region_file, flag_end_size):
    """Validate input file and output a validated version

    NOTE: the validated file (LOOP_OUT_FILE) may be unchanged from the original."""

    # Print params
    print(f"Input loop file: {loop_in_file}")
    print(f"Output loop file: {loop_out_file}")
    print(f"Chromosome regions file: {chromosome_region_file}")
    print(f"Flagging loop ends that are >= {flag_end_size:e}")
    print(f"Delimiter for output: '{common.delimiter}'")

    # Read in loop data
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=common.detect_delimiter(loop_in_file))

    # Read in chromosome regions
    chr_rg = pd.read_table(chromosome_region_file, header=None, delimiter=common.detect_delimiter(chromosome_region_file))

    # Sort loop_in
    # Note: sorting by: col 0, 1, then 2
    loop_in[0] = pd.Categorical(loop_in[0], chr_rg[0])
    loop_in = loop_in.sort_values(by=[0, 1, 2], ignore_index=True)
    loop_in[0] = loop_in[0].astype("object")

    # Validate loop data
    loop_out = validate_loop_in(loop_in, flag_end_size)

    # Output data
    loop_out.to_csv(loop_out_file, header=None, index=None, sep=common.delimiter)
    print(f"Validated data outputted to file {loop_out_file}")


def validate_loop_in(loop_in, flag_end_size):
    """Validate input loop with the following criteria (per row):
    1) Check if start size and end size are the same (if V6-V5 = V3-V2), if not -> issue warning
    2) Check that V3 > V2 and V6 > V5, if not -> issue warning
    3) Check that start and end do not overlap (if V5 > V3), if they do -> issue warning
    4) Check that the position of end > position of start (only if not caught already on other errors), if not -> issue warning & swap start with end
    5) Check if long-distance (loop that starts and ends in different chromosomes), if so -> remove affected row & issue warning
    6) Check that no loop distance is >100K, if so -> remove affected row & issue warning
    """
    print("Validating loop data")
    loop_in_validated = loop_in.apply(validate_row, axis="columns", args=(flag_end_size,)).dropna()
    print("Validation complete")
    return loop_in_validated


def validate_row(row, flag_end_size):
    row[1], row[2], row[4], row[5] = int(row[1]), int(row[2]), int(row[4]), int(row[5])
    row_num = row.name + 1  # Count from 1 for ease of use
    error_found = False
    first_end_len = row[2] - row[1]
    second_end_len = row[5] - row[4]
    # 1
    if first_end_len != second_end_len:
        print(f"WARNING: sizes of first and second end of loop differ ({first_end_len} != {second_end_len}) on row {row_num}")
        error_found = True
    # 2
    if row[1] >= row[2]:
        print(f"WARNING: first end of loop has start >= end ({row[2]} >= {row[1]}) on row {row_num}")
        error_found = True
    # 2
    if row[4] >= row[5]:
        print(f"WARNING: second end of loop has start >= end ({row[4]} >= {row[5]}) on row {row_num}")
        error_found = True
    # 3
    if row[2] >= row[4]:
        print(f"WARNING: first and second end of loop overlap ({row[2]} >= {row[4]}) on row {row_num}")
        error_found = True
    if not error_found:
        # 4
        remove_row = False
        if row[5] < row[1]:
            print(f"WARNING: Second end of loop comes before first end [{row[1:3]} > {row[4:]}] on row {row_num}")
            print(f"swapping first and second ends...")
            old_start = row[:3]
            old_end = row[3:]
            row[:3] = old_end
            row[3:] = old_start
        # 5
        if row[0] != row[3]:
            print(f"WARNING: long-distance loop detected ({row[0]} != {row[3]}) on row {row_num}")
            print(f"removing row...")
            remove_row = True
        # 6
        if first_end_len >= flag_end_size:
            print(f"WARNING: first end of loop exceeds {flag_end_size:e} ({first_end_len} >= {flag_end_size}) on row {row_num}")
            print(f"removing row...")
            remove_row = True
        # 6
        if second_end_len >= flag_end_size:
            print(f"WARNING: second end of loop exceeds {flag_end_size:e} ({second_end_len} >= {flag_end_size}) on row {row_num}")
            print(f"removing row...")
            remove_row = True
        if remove_row:
            row[0] = np.NaN
    return row
