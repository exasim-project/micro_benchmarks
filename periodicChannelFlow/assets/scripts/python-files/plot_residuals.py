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

# --- load data into df
# get all filenames for current field
files = glob.glob('./postProcessing/solverInfo/*/solverInfo.dat')
# sort files based on time driectory
files.sort(key=lambda x: x.split('/')[-2])
# get column names from header
headers = pd.read_csv(files[-1],sep='\t',skiprows=1, nrows=0).columns.str.strip('# ')
# load data
df = pd.concat((pd.read_csv(filename,sep='\t',comment='#',header=None, names=headers) for filename in files),ignore_index=True)

ax = df.plot.line(x='Time',y=[col for col in df.columns if 'initial' in col],logy=True,ylabel='initial residual')
ax.set_ylim([1e-10,1])
plt.savefig('../plots/fig_solverInfo_initialResidual.png',dpi=450, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='Time',y=[col for col in df.columns if 'final' in col],logy=True,ylabel='final residual')
ax.set_ylim([1e-10,1])
plt.savefig('../plots/fig_solverInfo_finalResidual.png',dpi=450, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='Time',y=[col for col in df.columns if 'iters' in col],logy=True,ylabel='linear iterations')
ax.set_ylim([1,50])
plt.savefig('../plots/fig_solverInfo_iters.png',dpi=450, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

plt.close('all')
