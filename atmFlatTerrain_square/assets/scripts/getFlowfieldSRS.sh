#!/bin/sh
# Download and unpack initial flow field
wget "https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EervfwixEExDsOVlGhucRpgB61RCSN7NL6eR81Z3YGBB-w?download=1" -O atmFlatTerrain_square_restart_SRS_t2000s.tar.gz
tar -xvzf atmFlatTerrain_square_restart_SRS_t2000s.tar.gz
rm -rf atmFlatTerrain_square_restart_SRS_t2000s.tar.gz
