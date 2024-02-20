#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EZLK28z2pupIlSLnOlb7fjsBYmH0VHttF3sIZZ-O0T9J-Q?download=1 -O impingingJet_LES_restart.tar.gz
tar -xvzf impingingJet_LES_restart.tar.gz
rm -rf impingingJet_LES_restart.tar.gz
