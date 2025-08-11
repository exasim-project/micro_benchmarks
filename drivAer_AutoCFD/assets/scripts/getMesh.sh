#!/bin/sh
# Download and unpack grid
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EX1vRcX_jqFIjfMld3GuZfgB7KVM9jOg54pZHLUTzvLzBQ?download=1 -O polyMesh.tar.gz
tar -xvzf polyMesh.tar.gz
mv polyMesh constant
rm -rf polyMesh.tar.gz
