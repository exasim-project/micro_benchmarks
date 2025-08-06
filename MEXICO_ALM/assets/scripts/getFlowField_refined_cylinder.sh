#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/ERZjY7EBZuJDo3Z7WhvZVCgBHUv9aP-AIB6bRqPugoGTkg?download=1 -O initialField.tar.gz
tar -xvzf initialField.tar.gz
rm -rf initialField.tar.gz
