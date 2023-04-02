"""loop simulation"""

import multiprocessing as mp
import os

import click
import numpy as np
import pandas as pd

from . import common


@click.command()
@click.argument("loop_in_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("chromosome_region_file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument("simulation_data_directory", type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True))
@click.option("--num-sims", show_default=True, default=1, type=int, help="number of simulations")
@click.option(
    "--num-processes",
    type=int,
    help="number of threads to use                          [default: round(multiprocessing.cpu_count() / 2)]",
)
def simulate(loop_in_file, chromosome_region_file, simulation_data_directory, num_sims, num_processes):
    """Generate a distribution of simulations

    NOTE: any data in SIMULATION_DATA_DIRECTORY may be overwritten!!"""
    # Set number of processes if not passed in by user
    if num_processes is None:
        num_processes = round(mp.cpu_count() / 2)

    # Get data dir sorted out
    if not os.path.isdir(simulation_data_directory):
        print("Simulation data directory does not exist.")
        os.makedirs(simulation_data_directory)
        print("Simulation data directory created!")

    # Print params
    print(f"Input loop file: {loop_in_file}")
    print(f"Chromosome regions file: {chromosome_region_file}")
    print(f"Number of simulations: {num_sims}")
    print(f"Number of processes: {num_processes}")
    print(f"Outputting simulation files to directory: {simulation_data_directory}")
    print(f"Delimiter for output: '{common.delimiter}'")

    # Read in loop data
    loop_in = pd.read_table(loop_in_file, header=None, delimiter=common.detect_delimiter(loop_in_file))

    # Read in chromosome regions
    chr_rg = pd.read_table(chromosome_region_file, header=None, delimiter=common.detect_delimiter(chromosome_region_file))

    # Multiprocessing
    sim_names = range(num_sims)
    with mp.Pool(num_processes) as pool:
        completed_sims = pool.starmap(run_sim, [(loop_in, chr_rg, sim_name) for sim_name in sim_names])

    # Output simulated loop data to files
    for sim, sim_name in zip(completed_sims, sim_names):
        output_filepath = f"{simulation_data_directory}/sim_hi-c_{sim_name}.loop"
        sim.to_csv(output_filepath, header=None, index=None, sep=common.delimiter)
        print(f"Simulation {sim_name} data outputted to file: {output_filepath}")


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
