import multiprocessing
import sys

import numpy as np
import pandas as pd


def main():
    # Read in loop data
    loop_in = pd.read_table("merged_5K_10K.loop", header=None)

    # Read in chromosome regions
    chr_rg = pd.read_table("chr_region_hg19", header=None, delimiter=" ")

    # CLI args
    num_processes = sys.argv[1] if len(sys.argv) > 1 else 1
    print(f"Running {num_processes} processes.")

    # Multiprocessing
    jobs = []
    for process_name in range(num_processes):
        p = multiprocessing.Process(name=str(process_name), target=run_sim, args=(loop_in, chr_rg))
        jobs.append(p)
        p.start()


def run_sim(loop_in, chr_rg):
    """Run simulation on all chromosomes"""
    process_name = multiprocessing.current_process().name

    # Run simulation
    print(f"Process {process_name} simulation started.")
    loop_out = split_by_chr(loop_in).apply(sim_chromosome, chr_rg=chr_rg)
    print(f"Process {process_name} simulation complete.")

    # Output simulated loop data to file
    output_filepath = f"out/sim_hic_5K_10K-{process_name}.loop"
    loop_out.to_csv(output_filepath, header=None, index=None)
    print(f"Process {process_name} data outputted to file {output_filepath}.")


def split_by_chr(in_loop: pd.DataFrame):
    """Split dataframe by chromosome"""
    return in_loop.groupby(0, sort=False)


def sim_chromosome(loop_chr_in: pd.DataFrame, chr_rg: pd.DataFrame):
    """Run simulation on a single chromosome
    Takes in a dataframe composed of all the rows for a single chromosome
    and a dataframe of chromosome regions
    """
    chr = loop_chr_in.loc[loop_chr_in.first_valid_index(), 0]  # Get the chromosome number

    a = chr_rg[chr_rg[0] == chr]  # Region num for current chromosome
    ran = int(a[2])  # ! Need this or pandas does weird things

    # The output df should have the same dimensions as the input df
    loop_chr_out = pd.DataFrame(np.empty(loop_chr_in.shape))

    # Fill in the first row
    loop_chr_out.loc[loop_chr_in.first_valid_index()] = sim_chromosome_helper(
        chr,
        ran,
        res=loop_chr_in.loc[loop_chr_in.first_valid_index(), 2] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
        len_=loop_chr_in.loc[loop_chr_in.first_valid_index(), 4] - loop_chr_in.loc[loop_chr_in.first_valid_index(), 1],
    )

    # Fill in the rest of the rows
    rows_in = loop_chr_in.itertuples(index=False)
    prev_row_in = next(rows_in)
    prev_row_out = loop_chr_out.loc[loop_chr_in.first_valid_index()]
    for idx, row_in in enumerate(rows_in):  # Will start at 2nd row
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
                res=row_in[2] - row_in[1],
                len_=row_in[4] - row_in[1],
            )
        loop_chr_out.loc[idx] = row_out
        prev_row_in, prev_row_out = row_in, row_out

    return loop_chr_out


def sim_chromosome_helper(chr, ran, res, len_):
    end1 = np.random.choice(np.arange((1 + res / 2), (ran - res / 2 - len_)))
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
