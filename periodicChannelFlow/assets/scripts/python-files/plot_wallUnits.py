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
    files = glob.glob(f'./postProcessing/{path}/*/lineR_pMean_pPrime2Mean_UMean_UPrime2Mean.xy')
    files.sort(key=lambda x: x.split('/')[-2])  # Sort by time directory

    # Get column names from the last file (assumes consistent format)
    #headers = pd.read_csv(files[-1], sep='\t', skiprows=4, nrows=0).columns.str.strip('# ')
    headers = ["y","pMean","pPrime2Mean","Ux","Uy","Uz","uu","vv","ww","uv","uw","vw"]

    # Load data into DataFrame
    df = pd.concat(
        (pd.read_csv(filename, sep='\t', comment='#', header=None, names=headers) for filename in files),
        ignore_index=True
    )

    Retau=363.6

    # Convert 'areaAverage(U)' column from string to NumPy array
    #df['areaAverage(U)'] = df['areaAverage(U)'].str.replace(' ', ',').apply(ast.literal_eval).apply(np.asarray)

    df['yplus'] = df['y'].apply(lambda u: u*Retau)
    df['pRMS'] = df['pPrime2Mean'].apply(lambda u: np.sqrt(u))
    df['Urms'] = df['uu'].apply(lambda u: np.sqrt(np.abs(u)))
    df['Vrms'] = df['vv'].apply(lambda u: np.sqrt(np.abs(u)))
    df['Wrms'] = df['ww'].apply(lambda u: np.sqrt(np.abs(u)))

    return df

def load_ref(path):
    DNS = {}
    DNS['mean'] = np.genfromtxt(f'{path}/spectralDNS/mean.dat')
    DNS['var'] = np.genfromtxt(f'{path}/spectralDNS/var.dat')

    # extract some data from the DNS case array, so that they have the same
    # structure as the OpenFOAM case
    ny = DNS['mean'][:,0].size
    DNS['U'] = DNS['mean'][1:(ny-3)//2+1,0:2]
    DNS["u'"] = DNS['var'][1:(ny-3)//2+1,0:2];    DNS["u'"][:,1] = DNS["u'"][:,1]**0.5
    DNS["v'"] = DNS['var'][1:(ny-3)//2+1,[0,2]];  DNS["v'"][:,1] = DNS["v'"][:,1]**0.5
    DNS["w'"] = DNS['var'][1:(ny-3)//2+1,[0,3]];  DNS["w'"][:,1] = DNS["w'"][:,1]**0.5

    # some bulk statistics of the spectral DNS case
    DNS['delra_ni'] = 0.00275052
    DNS['utau'] = 0.05275557

    # import data of ISTM OpenFOAM run
    OpenFOAM = {}
    OpenFOAM['U']      = np.loadtxt(f'{path}/ISTMopenFOAMrun/Uf.xy', dtype=np.float64)
    OpenFOAM["u'"] = np.loadtxt(f'{path}/ISTMopenFOAMrun/u.xy', dtype=np.float64)
    OpenFOAM["v'"] = np.loadtxt(f'{path}/ISTMopenFOAMrun/v.xy', dtype=np.float64)
    OpenFOAM["w'"] = np.loadtxt(f'{path}/ISTMopenFOAMrun/w.xy', dtype=np.float64)
    # some bulk statistics of the ISTM OpenFOAM run
    PGOF = np.genfromtxt(f'{path}/ISTMopenFOAMrun/pGrad.txt')
    MPGOP = np.average(PGOF)
    OpenFOAM['utau'] = np.sqrt(MPGOP)
    OpenFOAM['nu'] = 1.45105e-04
    OpenFOAM['delta_ni'] = OpenFOAM['nu']/OpenFOAM['utau']
    return DNS,OpenFOAM

DNS,OpenFOAM = load_ref("../../../benchmarkData")
# Load data 
df = load_data('sampleDict_line')

ax = df.plot.line(x='yplus', y='pMean', color='#1C81AC',logx=True,xlabel=r"$y^+'$",ylabel=r'$\overline{p}$')

# Save the figure
plt.savefig('../plots/fig_sample_pMean.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='yplus', y='pRMS', color='#1C81AC',logx=True,xlabel=r"$y^+'$",ylabel=r"$\overline{p}'$")

# Save the figure
plt.savefig('../plots/fig_sample_pRMS.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='yplus', y='Ux', color='#1C81AC', label='Current',logx=True,xlabel=r"$y^+'$",ylabel=r"$\overline{U}/U_b$", zorder=2)
ax.plot(363.6*DNS['U'][2:,0], DNS['U'][2:,1], 'k.', label='Spectral DNS', zorder=1)
ax.legend()

# Save the figure
plt.savefig('../plots/fig_sample_UMean.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='yplus', y='Urms', color='#1C81AC', label='Current',logx=True,xlabel=r"$y^+'$",ylabel=r"$\overline{U}_{rms}/U_b$", zorder=2)
ax.plot(363.6*DNS["u'"][2:,0], DNS["u'"][2:,1], 'k.', label='Spectral DNS', zorder=1)
ax.legend()

# Save the figure
plt.savefig('../plots/fig_sample_Urms.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

ax = df.plot.line(x='yplus', y='Vrms', color='#1C81AC', label='Current',logx=True,xlabel=r"$y^+'$",ylabel=r"$\overline{V}_{rms}/U_b$", zorder=2)
ax.plot(363.6*DNS["v'"][2:,0], DNS["v'"][2:,1], 'k.', label='Spectral DNS', zorder=1)
ax.legend()

# Save the figure
plt.savefig('../plots/fig_sample_Vrms.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)
#ax.plot(OpenFOAM['U'][:, 0], OpenFOAM['U'][:, 1], 'ko', label='OpenFoam ISTM')

ax = df.plot.line(x='yplus', y='Wrms', color='#1C81AC', label='Current',logx=True,xlabel=r"$y^+'$",ylabel=r"$\overline{W}_{rms}/U_b$", zorder=2)
ax.plot(363.6*DNS["w'"][2:,0], DNS["w'"][2:,1], 'k.', label='Spectral DNS', zorder=1)
ax.legend()

# Save the figure
plt.savefig('../plots/fig_sample_Wrms.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)


plt.close('all')
