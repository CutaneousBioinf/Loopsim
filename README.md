# Hi-C

## TODO: 

- [x] Update instructions

## Running the simulation

First, you'll need to create and activate the conda environment.

```console
$ conda env create -f environment.yml
$ conda activate hi-c
```

To run the simulation:

```console
$ ./sim_hic_loop.py --help
Usage: sim_hic_loop.py [OPTIONS] LOOP_IN_FILE CHROMOSOME_RG_FILE

Options:
  --num-sims INTEGER       number of simulations  [default: 1]
  --num-processes INTEGER  number of threads to use
                           [default: round(multiprocessing.cpu_count() / 2)]
  --out-dir DIRECTORY      directory for simulated data  [default: ./out]
  --output-delimiter TEXT  delimiter for the output file [default: tab]
  --flag-end-size INTEGER  warn on loop ends that are sized >= this param
                           [default: 100000]
  --help                   Show this message and exit.
```

For each simulation, the program will generate a simulated loop file (`sim_hi-c_<simulation number>.loop`) in `out_dir`.

If `out_dir` does not exist already, it will be created.

### Short tutorial

> Note: depending on the specs of your machine, this may take some time to run.

Running one simulation with the provided input files:

```console
$ conda activate hi-c
$ ./sim_hic_loop.py merged_5K_10K.loop chr_region_hg19
Input loop file: merged_5K_10K.loop
Chromosome regions file: chr_region_hg19
Number of simulations: 1
Number of processes: 6
Outputting simulation files to directory: ./out.
Delimiter for output: ' '
Flagging loop ends that are >= 1.000000e+05
Validating loop data
Validation complete
Simulation 0 simulation started
Simulation 0 simulation complete
Simulation 0 data outputted to file: ./out/sim_hi-c_0.loop
```

You should have something like the following.

```
.
└── out
    └── sim_hi-c_0.loop
```

```console
$ head ./out/sim_hi-c_0.loop
1       84173524.0      84183524.0      1       84313524.0      84323524.0
1       84833524.0      84843524.0      1       84943524.0      84953524.0
1       84993524.0      85003524.0      1       85093524.0      85103524.0
1       85248524.0      85258524.0      1       85363524.0      85373524.0
1       85253524.0      85263524.0      1       85638524.0      85648524.0
1       85253524.0      85263524.0      1       85443524.0      85453524.0
1       85263524.0      85273524.0      1       85613524.0      85623524.0
1       85308524.0      85318524.0      1       85348524.0      85358524.0
1       85453524.0      85463524.0      1       85593524.0      85603524.0
1       85468524.0      85478524.0      1       85823524.0      85833524.0
```
