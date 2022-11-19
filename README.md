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
$ python3 sim_hic_loop.py [num_simulations] [output_dir]
```

For each simulation, the program will generate a simulated loop file (`sim_hic_5K_10K-<simulation number>.loop`) in `output_dir`.

If `output_dir` does not exist already, it will be created.

The arguments `num_simulations` and `output_dir` are optional.
If they are not given, the program will default to the following.

```console
$ python3 sim_hic_loop.py 1 out/
```

### Short tutorial

> Note: depending on the specs of your machine, this may take some time to run.

Running one simulation with the provided input files:

```console
$ conda activate hi-c
$ python3 sim_hic_loop.py
Running 1 simulations in 1 processes.
Creating output directory out.
Outputting simulation files to directory out.
Process 0 simulation started.
Process 0 simulation complete.
Process 0 data outputted to file out/sim_hic_5K_10K-0.loop.
```

You should have something like the following.

```
.
└── out
    └── sim_hic_5K_10K-0.loop
```

```console
$ head out/sim_hic_5K_10K-0.loop
1       96214354.0      96224354.0      1       96324354.0      96334354.0
1       96374354.0      96384354.0      1       96474354.0      96484354.0
1       96629354.0      96639354.0      1       96744354.0      96754354.0
1       96634354.0      96644354.0      1       97019354.0      97029354.0
1       96634354.0      96644354.0      1       96824354.0      96834354.0
1       96644354.0      96654354.0      1       96994354.0      97004354.0
1       96689354.0      96699354.0      1       96729354.0      96739354.0
1       96834354.0      96844354.0      1       96974354.0      96984354.0
1       96849354.0      96859354.0      1       97204354.0      97214354.0
1       96884354.0      96894354.0      1       97824354.0      97834354.0
```
