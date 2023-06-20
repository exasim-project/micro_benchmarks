#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:f:/g/personal/louis_fliessbach_upstream-cfd_com/EbaA407ZpRFHqKfMx062SeIBAEMrALNvDPCJuE-oETbCbg?download=1 -O windsorBodyDDESInitField.tar.gz
tar -xvzf windsorBodyDDESInitField.tar.gz
rm -rf windsorBodyDDESInitField.tar.gz