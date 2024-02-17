# Micro Benchmarks
A collection of OpenFOAM cases to benchmark in the exasim project.
The following cases are available:
* **LidDrivenCavity3D**: Reusage of case from OpenFOAM HPC Technical Committee [HPC-Benchmark-Suite](https://develop.openfoam.com/committees/hpc#openfoam-hpc-benchmark-suite)
* **WindsorBody**: Case 1 from [AutoCFD4-Workshop](https://autocfd.eng.ox.ac.uk/) coarse mesh 
* **PeriodicChannelFlow**: Re=400, Lx=0.75, Lz=0.4
* **atmFlatTerrain**: Athmospheric boundary layer over flat terrain
* **ImpingingJet**: Reproduction of DNS case of [Dairay et al. (2015), Journal of Fluid Mechanics 764, pp. 362 - 394](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/abs/direct-numerical-simulation-of-a-turbulent-jet-impinging-on-a-heated-wall/0286E7962BABF0CCE6FD2862BCAA57DF)
The following case additioanlly tested within EXASIM contains a proprietary airfoil shape and is only shared with the partners. Contact: [Hendrik Hetmann](mailto:hendrik.hetmann@upstream-cfd.com). A non-proprietary version might be uploaded here in the future.
* **MexicoRotor**: Reproduction of MexicoRotor wind tunnel tests [K. Boorsma, J.G. Schepers (2014), New Mexico Experiment: Preliminary Overview with Initial Validation, ECN Edition 15, Vol.48](https://publications.tno.nl/publication/34629288/1z9HK6/e14048.pdf)

# Usage
It is recommended to use [OBR](https://github.com/hpsim/OBR) to setup the cases. This is a tool to automatically setup and run large OpenFOAM parameter studies based on the data structuring software [signac](https://docs.signac.io/en/latest/projects.html). On HPC clusters it is recommended to setup the and run the cases using the cluster submission functionality, this way creating cases can be distributed over many compute nodes. In the following this shown for the HoReKa supercomputer and the WindsorBody case.

    obr init -c <PATH_TO_YAML>
    obr run -o fetchCase
    # Run the mesh concatenation
    obr submit \
      --operation shell \
      --partition cpuonly \
      --template $EXASIM_MICROBENCHMARKS/scheduler_templates/horeka.sh \
      --time 60 \
      --scheduler_args "tasks_per_node 76"
    # Run the mesh decomposition
    obr submit \
      --operation decomposePar \
      --partition cpuonly \
      --template $EXASIM_MICROBENCHMARKS/scheduler_templates/horeka.sh \
      --time 60 \
      --scheduler_args "tasks_per_node 76"
    # Setup the solver. Can be done locally since not many compute resouces are needed
    obr run -o fvSolution 

## Submission examples

On HoReKa the jobs can be submitted based on the desired partition. An example for the cpu partition is given next

    obr submit \
       -o runParallelSolver 
       --filter solver==PCG \
       --partition cpuonly \
       --time 240 \
       --template $EXASIM_MICROBENCHMARKS/scheduler_templates/horeka.sh \
       --scheduler_args "tasks_per_node 76"


# Structure
Each micro-benchmark is stored in a subdirectory. In each case directory there is an additional subdirectory `basicSetup` containing the OpenFOAM setup and a subdirectory `assets` containing YAML files describing parameter or scaling studies, as well as post-processing scripts or reference data.

    <Casename>/
    |___ basicSetup/
    |              |___ 0.orig/
    |              |___ constant/
    |              |___ system/
    |___ assets/
               |___ scripts/
               |___ scaling.yaml

Additionally the repositary contains a subdirectory `common`, which includes YAML setup snippets for different parameter changes e.g. domain decomposition, solver choice and blockMesh resolution.
The directory `scheduler_templates` contains examples for cluster submission templates used with [OBR](https://github.com/hpsim/OBR).
The `Allrun` script contains an example workflow how to setup a case with OBR, run it on a cluster and do post-processing and archieving. 

