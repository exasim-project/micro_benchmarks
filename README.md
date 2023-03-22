# Micro Benchmarks
A collection of OpenFOAM cases to benchmark in the exasim project

# Usage
All micro benchmarks are stored in subfolders, the assets subfolder 
contains several yaml files describing scaling benchmark setups. It 
is recommended to use [OBR](https://github.com/hpsim/OBR) to setup the cases,
to avoid setting up the test matrix manually.


# Enviroment Variables

	export GINKGO_EXECUTOR=hip
	export NCPUS=32 # set it to 4 so that 8 * NCPUS gives a full node
	export NGPUS=8 # 8 set it to one since we cant scale accross multiple nodes on this machine
	export NCPUS_PER_GPU=4 # 8 set it to one since we cant scale accross multiple nodes on this machine
	export NCPU_PER_GPU=4 # 8 set it to one since we cant scale accross multiple nodes on this machine
	export NNODES=1
	export EXASIM_SYSTEM_NAME=nla
	export EXASIM_DATA_REPOSITORY=/home/greole/data/code/exasim_project/benchmark_data
	export OBR_RUN_CMD="mpirun --bind-to core --map-by core -np {np} {solver} -parallel -case {path}/case >  {path}/case/{solver}_{timestamp}.log 2>&1"
