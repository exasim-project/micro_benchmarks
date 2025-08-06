#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EXoNstldrUdJm7HEMcN2CPAB4VsxLDE4pJMDQTYI7FSusg?download=1 -O initialField.tar.gz
tar -xvzf initialField.tar.gz
rm -rf initialField.tar.gz
