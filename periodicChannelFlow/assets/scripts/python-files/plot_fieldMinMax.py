#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2023, Upstream CFD
Description:
    Script to plot min/max values from OpenFOAM function object fieldMinMax

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

# --- initialise dictionaries and dataframe
# list of field entries to search for
fields = ['p', 'U']

# list of values to grep
values = ['Time', 'field', 'min', 'location(min)', 'processor(min)', 'max', 'location(max)', 'processor(max)']
columns = pd.MultiIndex.from_product([fields,values])

dfs_tmp = {}
# load data into df
for field in fields:
    # get all filenames for current field
    files = glob.glob('./postProcessing/minMax_'+field+'/*/fieldMinMax.dat')
    if len(files) == 0:
        continue
    # sort files based on time driectory
    files.sort(key=lambda x: x.split('/')[-2])

    dfs_tmp[field] = pd.concat((pd.read_csv(filename,sep='\t',comment='#',header=None, names=values) for filename in files),ignore_index=True)

    # convert type of column with location vector from string to array
    dfs_tmp[field]['location(min)'] = dfs_tmp[field]['location(min)'].str.replace(' ',',').apply(ast.literal_eval).apply(np.asarray)
    dfs_tmp[field]['location(max)'] = dfs_tmp[field]['location(max)'].str.replace(' ',',').apply(ast.literal_eval).apply(np.asarray)
df = pd.concat(dfs_tmp,axis=1)

for field in df.columns.levels[0]:
    ax1 = df[field].plot.line(x='Time',y=['min'],color='#1C81AC',legend=False)
    ax1.set_ylabel(f"min({field})",color='#1C81AC')
    ax1.tick_params(axis='y', colors='#1C81AC')
    iterLimits = 10
    delta = df[field]['min'][iterLimits:].max()-df[field]['min'][iterLimits:].min()
    minLim = df[field]['min'][iterLimits:].min() - 0.2*(delta+0.001)
    maxLim = df[field]['min'][iterLimits:].max() + 0.2*(delta+0.001)
    ax1.set_ylim([minLim, maxLim])

    ax2 = df[field].plot.line(x='Time',y=['max'],secondary_y=True, ax=ax1,color='#EAB30E',legend=False)
    ax2.set_ylabel(f"max({field})",color='#EAB30E')
    ax2.tick_params(axis='y', colors='#EAB30E')
    delta = df[field]['max'][iterLimits:].max()-df[field]['max'][iterLimits:].min()
    minLim = df[field]['max'][iterLimits:].min() - 0.2*(delta+0.001) 
    maxLim = df[field]['max'][iterLimits:].max() + 0.2*(delta+0.001)
    ax2.set_ylim([minLim, maxLim])

    plt.savefig('../plots/fig_minMax-'+field+'.png',dpi=450, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)
plt.close('all')
