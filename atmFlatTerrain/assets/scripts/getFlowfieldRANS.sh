#!/bin/sh
# Download and unpack initial flow field
wget "https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/ETl7BriLmDFIiDB2yGQyMI8BDXf-V-RfYCJdN6mTTUgD8g?download=1" -O atmFlatTerrain_square_restart_RANS_t13000.tar.gz
tar -xvzf atmFlatTerrain_square_restart_RANS_t13000.tar.gz
rm -rf atmFlatTerrain_square_restart_RANS_t13000.tar.gz
