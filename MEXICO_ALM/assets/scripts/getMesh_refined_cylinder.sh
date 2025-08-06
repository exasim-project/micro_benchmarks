#!/bin/sh
# Download and unpack grid
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/Eb709Zk456lPjjEpCoKbTO0BWwVfnTN4YRO_Nwtxjdv_CQ?download=1 -O polyMesh.tar.gz
tar -xvzf polyMesh.tar.gz
mv polyMesh constant
rm -rf polyMesh.tar.gz
