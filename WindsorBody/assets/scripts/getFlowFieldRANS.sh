#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EYxc9Q3TH6VCmNzLxWXILZUBJpm40MEjjCFkD4Zp2QlVbg?download=1 -O WindsorBody_RANS_restart.tar.gz
tar -xvzf WindsorBody_RANS_restart.tar.gz
rm -rf WindsorBody_RANS_restart.tar.gz
