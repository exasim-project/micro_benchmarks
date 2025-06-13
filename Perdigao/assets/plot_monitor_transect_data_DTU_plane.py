#!/usr/bin/env python3

'''Script comparing mast measurement data with simulation for Perdigao site.'''

import sys, os
#from netCDF4 import Dataset
import numpy as np
import re
import itertools
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import vtk
from vtk.util.numpy_support import vtk_to_numpy

# UCFD colors
colors=[(1/255)*np.array([98,99,102]),(1/255)*np.array([28,129,172]),(1/255)*np.array([91,188,228]),(1/255)*np.array([97,191,128]),(1/255)*np.array([39,76,119]),(1/255)*np.array([33,104,105]),(1/255)*np.array([128,100,162]),(1/255)*np.array([247,150,70])]

__author__ = "Hendrik Hetmann"
__copyright__ = "Copyright 2024, Upstream CFD"
__license__ = "GPL"
__version__ = "0.0.0"
__email__ = "hendrik.hetmann@upstream-cfd.com"
__status__ = "Development"
__requires__ =""

def rotate(p, origin=(0, 0), degrees=0):
    angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)

rotation_center=[33830.57064749787, 4785.608784752652]

threshold_CNR_min = -25 	#DLR: -27, DTU: -25, CLAMPS: -23
threshold_CNR_max = 5

df_profil = pd.read_csv("../00_caseFiles/assets/Hoehenprofil_DTU.csv", sep = ';')
df_profil["coord"] = np.sqrt(df_profil['x'].mul(df_profil['x']) + df_profil['y'].mul(df_profil['y']))

df_WS1 = pd.read_csv("../00_caseFiles/assets/WS1_170510_1530.txt", sep=',', header = None)
df_WS1[7] = -df_WS1[7]
df_WS2 = pd.read_csv("../00_caseFiles/assets/WS2_170510_1530.txt", sep=',', header = None)
df_WS3 = pd.read_csv("../00_caseFiles/assets/WS3_170510_1530.txt", sep=',', header = None)
df_WS3[7] = -df_WS3[7]
df_WS4 = pd.read_csv("../00_caseFiles/assets/WS4_170510_1530.txt", sep=',', header = None)
df_all = pd.concat([df_WS1, df_WS2, df_WS3, df_WS4], axis=0).drop_duplicates()
df_all.columns = ["Time (UTC, '%y-%m-%d_%H:%M:%S.%f')", "Easting (m)", "Northing (m)", "Altitude (m)", "Azimuth (deg)", "Elevation (deg)", "Range (deg)", "Radial wind speed (m/s)", "CNR (dB)", "Radial wind speed dispersion (m/s)"]
#filter data
df_all = df_all[(df_all["CNR (dB)"] >= threshold_CNR_min) & (df_all["CNR (dB)"] <= threshold_CNR_max)]
#calculate velocity components
df_all["in plane velocity horiz [m/s]"] = np.divide(df_all["Radial wind speed (m/s)"], np.cos(df_all["Elevation (deg)"]*np.pi/180.0))
df_all["coord"] = np.sqrt(df_all["Easting (m)"].mul(df_all["Easting (m)"]) + df_all["Northing (m)"].mul(df_all["Northing (m)"]))

# Load VTK
latestTime=max([os.path.join("./postProcessing/cuttingPlanes/",d) for d in os.listdir("./postProcessing/cuttingPlanes/")], key=os.path.getmtime)
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(latestTime+"/DTU_plane.vtp")
reader.Update()

polydata = reader.GetOutput()
filt = vtk.vtkCellCenters()
filt.SetInputDataObject(polydata)
filt.Update()
pts=vtk_to_numpy(filt.GetOutput().GetPoints().GetData())
pts[:,0]=pts[:,0]+rotation_center[0]
pts[:,1]=pts[:,1]+rotation_center[1]
backrotated=rotate(pts[:,:2], origin=rotation_center, degrees=45)
pts[:,:2]=backrotated

U=vtk_to_numpy(filt.GetOutput().GetPointData().GetArray('U'))
coord_sim=np.sqrt(np.power(pts[:,0],2)+np.power(pts[:,1],2))
U_horz_sim=np.sqrt(np.power(U[:,0],2)+np.power(U[:,1],2))

#create plots
cm = plt.cm.get_cmap('inferno')

#fig = plt.figure(figsize=[16,8])
fig, axes = plt.subplots(2, 1, sharex=True)
ax=axes[0]
ax1=axes[1]
plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.3)
ax.set_ylabel('height [m]')
ax.set_xlim(32500, 36000)
ax.set_ylim(0, 1000)
#ax.set_aspect('equal', 'box')
ax.set_title('DTU Lidar data, Processing: N. Wildmann (DLR)',fontsize=10)
sc = ax.scatter(df_all['coord'], df_all["Altitude (m)"], c=df_all["in plane velocity horiz [m/s]"], s= 1.0, vmin=-15, vmax=15, cmap=cm, marker='s')
#plt.colorbar(sc, orientation="horizontal",fraction=0.04,anchor=(1.0,0.0))
#ax.scatter(df_masts['coord'], df_masts['z'], c='k', s=2)
ax.plot(df_profil['coord'], df_profil['z'], c='k')

#ax1 = fig.add_subplot(221)
ax1.set_xlabel('in plane coordinate [m]')
ax1.set_ylabel('height [m]')
ax1.set_xlim(32500, 36000)
ax1.set_ylim(0, 1000)
#ax1.set_aspect('equal', 'box')
ax1.set_title('EXASIM AC1 simulation',fontsize=10)
sc1 = ax1.scatter(coord_sim, pts[:,2], c=U_horz_sim, s=0.2 , vmin=-15, vmax=15, cmap=cm, marker='s')
#ax.scatter(df_masts['coord'], df_masts['z'], c='k', s=2)
ax1.plot(df_profil['coord'], df_profil['z'], c='k')


cb=fig.colorbar(sc1, ax=axes.ravel().tolist(), shrink=0.8,label="$U_{horz}$ [m/s]")
#cb.ax.set_title("$U_{horz}$ [m/s]",ha="left")
#plt.show()

fig.savefig("fig_monitor_DTU_plane.png", bbox_inches='tight',dpi=300)