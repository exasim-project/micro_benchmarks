#!/bin/bash
#SBATCH --job-name=Compile_OF
#SBATCH --time=01:30:00
#SBATCH --ntasks=76
#SBATCH --partition=cpuonly
#SBATCH --account=hk-project-exasim 

module purge
module load compiler/gnu/12
module load devel/cuda/12.2   

cd $HOME/OpenFOAM/openfoam

# Set WM_MPILIB to SYSTEMOPENMPI
sed -i 's/WM_MPLIB=[A-Z]*/WM_MPLIB=SYSTEMOPENMPI/g' etc/basrc 

source etc/bashrc

./Allwmake -j > $HOME/OpenFOAM/openfoam/build.log 2>&1 
