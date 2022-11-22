# Hi-C

## TODO: 

- [ ] Instructions on the rest of the pipeline

## Running the simulation

First, you'll need to create and activate the conda environment.

```console
$ conda env create -f environment.yml
$ conda activate hi-c
```

To run the simulation:

```console
$ ./sim_hic_loop.py --help
Usage: sim_hic_loop.py [OPTIONS] LOOP_IN_FILE

Options:
  --num_sims INTEGER   [default: 1]
  --out_dir DIRECTORY  [default: ./out]
  --help               Show this message and exit.
```

For each simulation, the program will generate a simulated loop file (`sim_hi-c_<simulation number>.loop`) in `out_dir`.

If `out_dir` does not exist already, it will be created.

### Short tutorial

> Note: depending on the specs of your machine, this may take some time to run.

Running one simulation with the provided input files:

```console
$ conda activate hi-c
$ ./sim_hic_loop.py merged_5K_10K.loop
Input loop file: merged_5K_10K.loop
Number of simulations: 1
Outputting simulation files to directory: ./out.
Simulation 0 simulation started.
Simulation 0 simulation complete.
Simulation 0 data outputted to file: ./out/sim_hi-c_0.loop.
```

You should have something like the following.

```
.
└── out
    └── sim_hi-c_0.loop
```

```console
$ head out/sim_hi-c_0.loop
1       52598173.0      52608173.0      1       52708173.0      52718173.0
1       52758173.0      52768173.0      1       52858173.0      52868173.0
1       53013173.0      53023173.0      1       53128173.0      53138173.0
1       53018173.0      53028173.0      1       53403173.0      53413173.0
1       53018173.0      53028173.0      1       53208173.0      53218173.0
1       53028173.0      53038173.0      1       53378173.0      53388173.0
1       53073173.0      53083173.0      1       53113173.0      53123173.0
1       53218173.0      53228173.0      1       53358173.0      53368173.0
1       53233173.0      53243173.0      1       53588173.0      53598173.0
1       53268173.0      53278173.0      1       54208173.0      54218173.0
```
