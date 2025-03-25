#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2023, Upstream CFD
Description:
    - script to plot residuals from OpenFOAM function object solverInfo
    - solverInfo writes the initial and final residual of the FIRST pimple iteration
    and only gives information about the convergence of the linear solver.

Author:
    Louis Fliessbach (louis.fliessbach@upstream-cfd.com)

last modified: 9.10.2023
"""

import os
import sys
import glob
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['agg.path.chunksize'] = 10000

def load_data(path):
    files = glob.glob(f'./postProcessing/{path}/*/surfaceFieldValue.dat')
    files.sort(key=lambda x: x.split('/')[-2])  # Sort by time directory

    # Get column names from the last file (assumes consistent format)
    headers = pd.read_csv(files[-1], sep='\t', skiprows=4, nrows=0).columns.str.strip('# ')

    # Load data into DataFrame
    df = pd.concat(
        (pd.read_csv(filename, sep='\t', comment='#', header=None, names=headers) for filename in files),
        ignore_index=True
    )

    #df['Urms'] = df['max(UPrime2Mean)'].apply(lambda u: np.sqrt(u))

    return df

# Load data 
df = load_data('wSS_top')

# Plot the averaged velocity
ax = df.plot.line(x='Time', y='areaAverage(wallShearStress)', color='#1C81AC', label='areaAverage(mag(wSS))',ylabel=r'$|\tau_w|$ [$m^2$/$s^2$]')
ax.set_ylim([0.001,0.005])
# Save the figure
plt.savefig('../plots/fig_wSS_top.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

plt.close('all')
