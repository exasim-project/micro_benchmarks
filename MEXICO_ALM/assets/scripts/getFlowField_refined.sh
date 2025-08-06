#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EWXhpNf9cwZBpGV4FyVRB0oBJ4f3dQcI83s7x2csNTPU2Q?download=1 -O initialField.tar.gz
tar -xvzf initialField.tar.gz
rm -rf initialField.tar.gz
