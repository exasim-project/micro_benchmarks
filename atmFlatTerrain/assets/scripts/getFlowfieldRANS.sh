#!/bin/sh
# Download and unpack initial flow field
wget "https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EYShwnz5G9pDjTGGyTDmL1oBW6s0Xutt5NRB3fLINSOk9Q?download=1" -O atmFlatTerrain_restart_RANS.tar.gz
tar -xvzf atmFlatTerrain_restart_RANS.tar.gz
rm -rf atmFlatTerrain_restart_RANS.tar.gz
