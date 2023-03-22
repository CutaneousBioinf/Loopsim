#!/usr/bin/env python3
"""Script to do Hi-C loop simulation"""

import multiprocessing as mp
import os

import click
import numpy as np
import pandas as pd
from detect_delimiter import detect


@click.command()
@click.argument("loop_in_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("chromosome_rg_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option("--num-sims", show_default=True, default=1, type=int, help="number of simulations")
@click.option(
    "--num-processes",
    type=int,
    help="number of threads to use                          [default: round(multiprocessing.cpu_count() / 2)]",
)
@click.option(
    "--out-dir",
    show_default=True,
    default="./out",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="directory for simulated data",
)
@click.option(
    "--output-delimiter",
    default="\t",
    type=str,
    help="delimiter for the output file [default: tab]",
)
@click.option(
    "--flag-end-size",
    show_default=True,
    default=100_000,
    type=int,
    help="warn on loop ends that are sized >= this param",
)
def main(loop_in_file, chromosome_rg_file, num_sims, num_processes, out_dir, output_delimiter, flag_end_size):
    # Create output directory if it doesn't exist
    if not os.path.isdir(out_dir):
        print(f"Output directory {out_dir} does not exist. Creating...")
        os.makedirs(out_dir)
        print(f"Created output directory {out_dir}.")

    # Set number of processes if not passed in by user
    if num_processes is None:
        num_processes = round(mp.cpu_count() / 2)

    # Print given arguments for a sanity check
    print(f"Input loop file: {loop_in_file}")
    print(f"Chromosome regions file: {chromosome_rg_file}")
    print(f"Number of simulations: {num_sims}")
    print(f"Number of processes: {num_processes}")
    print(f"Outputting simulation files to directory: {out_dir}.")
    print(f"Delimiter for output: '{output_delimiter}'")
    print(f"Flagging loop ends that are >= {flag_end_size:e}")

    # Read in loop data
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=detect_delimiter(loop_in_file))

    # Read in chromosome regions
    chr_rg = pd.read_table(chromosome_rg_file, header=None, delimiter=detect_delimiter(chromosome_rg_file))

    # Sort loop_in
    # Note: sorting by: col 0, 1, then 2
    loop_in[0] = pd.Categorical(loop_in[0], chr_rg[0])
    loop_in = loop_in.sort_values(by=[0, 1, 2], ignore_index=True)
    loop_in[0] = loop_in[0].astype("object")

    # Validate loop data
    loop_in = validate_loop_in(loop_in, flag_end_size)

    # Multiprocessing
    sim_names = range(num_sims)
    with mp.Pool(num_processes) as pool:
        completed_sims = pool.starmap(run_sim, [(loop_in, chr_rg, sim_name) for sim_name in sim_names])

    # Output simulated loop data to files
    for sim, sim_name in zip(completed_sims, sim_names):
        output_filepath = f"{out_dir}/sim_hi-c_{sim_name}.loop"
        sim.to_csv(output_filepath, header=None, index=None, sep=output_delimiter)
        print(f"Simulation {sim_name} data outputted to file: {output_filepath}")


def detect_delimiter(filename):
    with open(filename) as f:
        firstline = f.readline()
        return detect(firstline)


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
        print(
            f"WARNING: sizes of first and second end of loop differ ({first_end_len} != {second_end_len}) on row {row_num}"
        )
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
            print(
                f"WARNING: first end of loop exceeds {flag_end_size:e} ({first_end_len} >= {flag_end_size}) on row {row_num}"
            )
            print(f"removing row...")
            remove_row = True
        # 6
        if second_end_len >= flag_end_size:
            print(
                f"WARNING: second end of loop exceeds {flag_end_size:e} ({second_end_len} >= {flag_end_size}) on row {row_num}"
            )
            print(f"removing row...")
            remove_row = True
        if remove_row:
            row[0] = np.NaN
    return row


def run_sim(loop_in, chr_rg, sim_name):
    """Run simulation on all chromosomes"""
    print(f"Simulation {sim_name} simulation started")
    loop_out = split_by_chr(loop_in).apply(sim_chromosome, chr_rg=chr_rg)
    print(f"Simulation {sim_name} simulation complete")
    return loop_out


def split_by_chr(in_loop: pd.DataFrame):
    """Split dataframe by chromosome"""
    return in_loop.groupby(0, sort=False)


def sim_chromosome(loop_chr_in: pd.DataFrame, chr_rg: pd.DataFrame):
    """Run simulation on a single chromosome
    Takes in a dataframe composed of all the rows for a single chromosome
    and a dataframe of chromosome regions
    """
    # Fix: using the module level numpy random generates identical output in parallel processes
    # See https://github.com/numpy/numpy/issues/12231
    random_state = np.random.RandomState()

    chr = loop_chr_in.loc[loop_chr_in.first_valid_index(), 0]  # Get the chromosome number

    a = chr_rg[chr_rg[0] == chr]  # Region num for current chromosome
    ran = int(a[2])  # ! Need this or pandas does weird things

    # The output df should have the same dimensions as the input df
    loop_chr_out = pd.DataFrame(np.empty(loop_chr_in.shape), dtype=object)

    # Fill in the first row
    prev_row_out = loop_chr_out.loc[0] = sim_chromosome_helper(
        chr=chr,
        ran=ran,
        res=loop_chr_in.loc[loop_chr_in.first_valid_index(), 2] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
        len_=loop_chr_in.loc[loop_chr_in.first_valid_index(), 4] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
        random_state=random_state,
    )

    prev_row_in = loop_chr_in.loc[loop_chr_in.first_valid_index()]

    # Fill in the rest of the rows
    # Will start at 2nd row
    for iterations, row_in in enumerate(
        loop_chr_in.loc[loop_chr_in.first_valid_index() + 1 : loop_chr_in.last_valid_index() + 1].itertuples(index=False)
    ):

        dist = row_in[1] - prev_row_in[1]
        len_ = row_in[4] - row_in[1]
        res = row_in[5] - row_in[4]

        if dist < 10**6 and (prev_row_out[2] + dist) < ran and (prev_row_out[2] + dist + len_) < ran:
            row_out = [
                chr,
                prev_row_out[1] + dist,
                prev_row_out[1] + dist + res,
                chr,
                prev_row_out[1] + dist + len_,
                prev_row_out[1] + dist + len_ + res,
            ]
        else:
            row_out = sim_chromosome_helper(
                chr=chr,
                ran=ran,
                res=row_in[2] - row_in[1],
                len_=row_in[4] - row_in[1],
                random_state=random_state,
            )

        loop_chr_out.loc[iterations + 1] = row_out
        prev_row_in, prev_row_out = row_in, row_out

    return loop_chr_out


def sim_chromosome_helper(chr, ran, res, len_, random_state):
    end1 = random_state.choice(np.arange((1 + res / 2), (ran - res / 2 - len_)))
    end2 = end1 + len_
    return [
        chr,
        end1 - res / 2,
        end1 + res / 2,
        chr,
        end2 - res / 2,
        end2 + res / 2,
    ]


if __name__ == "__main__":
    main()
