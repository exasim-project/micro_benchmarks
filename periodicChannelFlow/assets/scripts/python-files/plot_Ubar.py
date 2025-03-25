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

    # Convert 'areaAverage(U)' column from string to NumPy array
    df['areaAverage(U)'] = df['areaAverage(U)'].str.replace(' ', ',').apply(ast.literal_eval).apply(np.asarray)

    # Extract first component (Ux)
    df['Ux'] = df['areaAverage(U)'].apply(lambda u: u[0])

    return df

# Load data from both inlet1 and inlet2
df1 = load_data('Ubar_inlet1')
df2 = load_data('Ubar_inlet2')

# Ensure both DataFrames are aligned (assuming they have the same 'Time' values)
df_avg = df1.copy()
df_avg['Ux'] = (df1['Ux'] + df2['Ux']) / 2  # Compute the average Ux

# Plot the averaged velocity
ax = df_avg.plot.line(x='Time', y='Ux', color='#1C81AC', label='areaAverage(Ux)',ylabel=r'$\overline{U}_x$ [m/s]')
ax.set_ylim([0.99,1.01])
# Save the figure
plt.savefig('../plots/fig_Ubar.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

plt.close('all')
