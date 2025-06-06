#!/usr/bin/env python3

'''Script comparing mast measurement data with simulation for Perdigao site.'''

import sys, os
#from netCDF4 import Dataset
import numpy as np
import re
import itertools
import pickle
import matplotlib.pyplot as plt

# UCFD colors
colors=[(1/255)*np.array([98,99,102]),(1/255)*np.array([28,129,172]),(1/255)*np.array([91,188,228]),(1/255)*np.array([97,191,128]),(1/255)*np.array([39,76,119]),(1/255)*np.array([33,104,105]),(1/255)*np.array([128,100,162]),(1/255)*np.array([247,150,70])]

__author__ = "Hendrik Hetmann"
__copyright__ = "Copyright 2024, Upstream CFD"
__license__ = "GPL"
__version__ = "0.0.0"
__email__ = "hendrik.hetmann@upstream-cfd.com"
__status__ = "Development"
__requires__ =""

def rotate(vec,deg):
    theta=np.deg2rad(deg)
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    return np.dot(rot, vec)

def loadprobes(filepath):
    with open(filepath,'r') as tmp_file:
        lines=tmp_file.readlines()
        lines=[line.replace('(','').replace(')','') for line in lines]
        tmp=np.loadtxt(lines,comments='#')
        t=tmp[:,0]
        #print(len(tmp[:,1:]))
        #print(tmp[:,1:].reshape(len(tmp[:,1:]),round(len(tmp[:,1:][0])/3),3))
        probes=tmp[:,1:].reshape(len(tmp[:,1:]),round(len(tmp[:,1:][0])/3),3)
    return t,probes

nSkip=0

file=open('../00_caseFiles/assets/mast_reference_data.dump', 'rb')
probes_meas=pickle.load(file)
file.close()
mastnamelist=['mast20','mast25','mast29','mast32','mast37']

probes_sim={}
probes_sim_horzWind={}
probes_meas_horzWind={}
for i in range(len(list(probes_meas.keys()))):
    path='./postProcessing/'+ mastnamelist[i]+'_'+list(probes_meas.keys())[i]+'/0/U'
    tmp_t,tmp_probes=loadprobes(path)
    probes_sim[list(probes_meas.keys())[i]]=np.mean(tmp_probes[nSkip:],axis=0)
    probes_sim_horzWind[list(probes_meas.keys())[i]]=np.sqrt(probes_sim[list(probes_meas.keys())[i]][:,0]**2+probes_sim[list(probes_meas.keys())[i]][:,1]**2)
    probes_meas_horzWind[list(probes_meas.keys())[i]]=[np.sqrt(element[0]**2+element[1]**2) for element in probes_meas[list(probes_meas.keys())[i]]]#np.sqrt(probes_meas[list(probes_meas.keys())[i]][:,0]**2+probes_meas[list(probes_meas.keys())[i]][:,1]**2)

mastids=list(probes_meas.keys())
diff_probes={}
for element in list(probes_meas.keys()):
    #diff_probes[element]=100*np.divide(probes_sim_horzWind[element]-probes_meas_horzWind[element],probes_meas_horzWind[element])
    diff_probes[element]=probes_sim_horzWind[element]-probes_meas_horzWind[element]
#print(diff_probes)
heights=np.array([20,40,60,80,100])

# ---- generate plot
# define plot and global font size
fig = plt.figure(num=0, figsize=(8.0,5.5), dpi=200)
plt.rcParams.update({'font.size': 12})
all_axes=fig.subplots(1,5,sharey=True)
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
for nn, ax4 in enumerate(all_axes):
    ax4.set_title(mastnamelist[nn]+'_'+mastids[nn],fontsize=9)
    ax4.grid()
    if nn==0:
        ax4.set_ylabel("Height [m]")
    if nn==2:
        ax4.set_xlabel("$\Delta U_{horz}$ [m/s]")
    if nn==3:
        heights=np.array([10,20])
    elif nn==4:
        heights=np.array([20,40,60])
    hU=ax4.barh(heights+1.5,diff_probes[mastids[nn]],2,color=colors[0])
    #hV=ax4.barh(heights,diff_probes[mastids[nn]][:,1],1,color=colors[1])
    #hW=ax4.barh(heights-1.5,diff_probes[mastids[nn]][:,2],1,color=colors[3])
    #if nn==4:
        #ax4.legend([hU,hV,hW],["u","v","w"],fontsize=12, loc=(1.01,0.6))
    ax4.set_xlim(-1.5, 1.5)
    ax4.set_xticks([-1.5,-1,-0.5,0,0.5,1,1.5])
    ax4.set_xticklabels([-1.5,-1,-0.5,0,0.5,1,1.5], rotation=-90, ha='center')

fig.suptitle("Simulation probes vs. mast measurements")
#plt.show()

# save figure
savestring = 'fig_monitor_delta_mast_data.png'
fig.savefig(savestring, dpi=200)
