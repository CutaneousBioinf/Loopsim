#!/usr/bin/env python3
"""Script to do Hi-C loop simulation"""

import multiprocessing
import os
import sys

import click
import numpy as np
import pandas as pd
from multiprocesspandas import applyparallel


@click.command()
@click.argument("loop_in_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option("--num_sims", show_default=True, default=1, type=int)
@click.option(
    "--out_dir", show_default=True, default="./out", type=click.Path(file_okay=False, dir_okay=True, writable=True)
)
def main(loop_in_file, num_sims, out_dir):
    # Create output directory if it doesn't exist
    if not os.path.isdir(out_dir):
        print(f"Output directory {out_dir} does not exist. Creating...")
        os.makedirs(out_dir)
        print(f"Created output directory {out_dir}.")

    # Print given arguments for a sanity check
    print(f"Input loop file: {loop_in_file}")
    print(f"Number of simulations: {num_sims}")
    print(f"Outputting simulation files to directory: {out_dir}.")

    # Read in loop data
    loop_in = pd.read_table(loop_in_file, header=None, delimiter="\t")

    # Read in chromosome regions
    chr_rg = pd.read_table("chr_region_hg19", header=None, delimiter=" ")

    # Multiprocessing
    sim_names = range(num_sims)
    with multiprocessing.Pool() as pool:
        completed_sims = pool.starmap(run_sim, [(loop_in, chr_rg, sim_name) for sim_name in sim_names])

    # Output simulated loop data to files
    for sim, sim_name in zip(completed_sims, sim_names):
        output_filepath = f"{out_dir}/sim_hi-c_{sim_name}.loop"
        sim.to_csv(output_filepath, header=None, index=None, sep="\t")
        print(f"Simulation {sim_name} data outputted to file: {output_filepath}.")


def run_sim(loop_in, chr_rg, sim_name):
    """Run simulation on all chromosomes"""
    print(f"Simulation {sim_name} simulation started.")
    loop_out = split_by_chr(loop_in).apply_parallel(sim_chromosome, chr_rg=chr_rg)
    print(f"Simulation {sim_name} simulation complete.")
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
        chr,
        ran,
        loop_chr_in.loc[loop_chr_in.first_valid_index(), 2] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
        loop_chr_in.loc[loop_chr_in.first_valid_index(), 4] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
        random_state,
    )

    prev_row_in = loop_chr_in.loc[loop_chr_in.first_valid_index()]

    # Fill in the rest of the rows
    for idx, row_in in enumerate(loop_chr_in.iloc[1:].itertuples(index=False)):  # Will start at 2nd row
        dist = row_in[1] - prev_row_in[1]
        len_ = row_in[4] - row_in[1]
        if dist < 10**6 and (prev_row_out[2] + dist) < ran and (prev_row_out[2] + dist + len_) < ran:
            row_out = [
                prev_row_out[0],
                prev_row_out[1] + dist,
                prev_row_out[2] + dist,
                prev_row_out[3],
                prev_row_out[1] + dist + len_,
                prev_row_out[2] + dist + len_,
            ]
        else:
            row_out = sim_chromosome_helper(
                chr,
                ran,
                row_in[2] - row_in[1],
                row_in[4] - row_in[1],
                random_state,
            )
        loop_chr_out.loc[idx] = row_out
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
