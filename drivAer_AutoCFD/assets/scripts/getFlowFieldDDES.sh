#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/hendrik_hetmann_upstream-cfd_com/EeH78TyJD8VMlVio9ZK2GskB8GDIwGx-pOz3Ob_iFox0Yw?download=1 -O drivAerDDESInitField.tar.gz
tar -xvzf drivAerDDESInitField.tar.gz
rm -rf drivAerDDESInitField.tar.gz
