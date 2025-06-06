#!/bin/sh
# Download and unpack initial flow field
wget https://upstreamcfdcom-my.sharepoint.com/:u:/g/personal/louis_fliessbach_upstream-cfd_com/EXwR5b2z0JdBtpjo7vDZAbgB0tblTnh80B6aeK7U1fIBKQ?download=1 -O windsorBodyDDESInitField.tar.gz
tar -xvzf windsorBodyDDESInitField.tar.gz
rm -rf windsorBodyDDESInitField.tar.gz