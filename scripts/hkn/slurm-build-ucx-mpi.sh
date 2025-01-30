#!/bin/bash
#SBATCH --job-name=build_ucx_ompi
#SBATCH --time=01:30:00
#SBATCH --ntasks=76
#SBATCH --partition=cpuonly
#SBATCH --account=hk-project-exasim 

module purge
module load compiler/gnu/12
module load devel/cuda/12.2   

# make sure $HOME/.local exists 
mkdir -p  $HOME/.local

# 
git clone https://github.com/openucx/ucx.git
cd ucx
./autogen.sh
./contrib/configure-release --disable-logging --disable-debug --disable-assertions --disable-params-check --host=x86_64-redhat-linux-gnu --program-prefix= --disable-dependency-tracking --prefix=$HOME/.local --disable-optimizations --disable-logging --disable-debug --disable-assertions --enable-mt --disable-params-check --without-go --without-java --enable-cma --with-cuda --with-gdrcopy --with-verbs --with-knem --with-rdmacm --without-rocm --with-xpmem --without-fuse3 --without-ugni --with-cuda=/software/all/devel/cuda/12.2
make -j
make install
cd ..

wget https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-5.0.6.tar.gz
tar xvf openmpi-5.0.6.tar.gz  
cd openmpi-5.0.6
./configure --prefix=$HOME/.local --with-cuda=/software/all/devel/cuda/12.2 --with-hwloc=/opt/hwloc/2.10 --with-hwloc-libdir=/opt/hwloc/2.10/lib --with-pmix=internal  --with-ucx=$HOME/.local --enable-mpi-thread-multiple --without-verbs --without-mxm --without-psm --without-psm2 --without-ofi --without-tm
make -j
make install

