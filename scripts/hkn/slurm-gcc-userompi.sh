#!/bin/bash
#SBATCH --job-name=Compile_OF
#SBATCH --time=01:30:00
#SBATCH --ntasks=76
#SBATCH --gpus-per-node=1
#SBATCH --partition=accelerated
#SBATCH --account=hk-project-exasim 

module purge
module load compiler/gnu/12
module load devel/cuda/12.2   
module load devel/cmake

source $HOME/OpenFOAM/openfoam/etc/bashrc

# cmake --preset release > config.log 2>&1

cmake --build --preset release > build.log 2>&1
cmake --build --preset release --target install
