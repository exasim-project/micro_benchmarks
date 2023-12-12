#!/usr/bin/python3

'''Script plotting scaling on AWS.'''

import sys, os
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np

# UCFD colors
colors=[(1/255)*np.array([98,99,102]),(1/255)*np.array([28,129,172]),(1/255)*np.array([91,188,228]),(1/255)*np.array([97,191,128]),(1/255)*np.array([39,76,119]),(1/255)*np.array([33,104,105]),(1/255)*np.array([128,100,162]),(1/255)*np.array([247,150,70])]

def loadprobes_perf_coeffs(filepath):
    tmp=np.loadtxt(filepath,comments='#', skiprows=0)
    x=tmp[:,2]
    u=tmp[:,3]
    v=tmp[:,4]
    w=tmp[:,5]
    return x,u,v,w

# Set path to log file
if len(sys.argv) > 1:
    path=os.getcwd() + '/' + sys.argv[1]
    z,u,v,w=loadprobes_perf_coeffs(path)

z_RANS,u_RANS,v_RANS,w_RANS=loadprobes_perf_coeffs("Leipzig_SST_RANS_Velocity_Ref.dat")
z_SRS,u_SRS,v_SRS,w_SRS=loadprobes_perf_coeffs("Leipzig_SST_SRS_Velocity_Ref.dat")
ref_data=np.loadtxt("Leipzig_reference.dat",comments='#', delimiter=',')

plt.rcParams.update({'font.size': 20})
fig=plt.figure(num=0,figsize=(8.0,6.0), dpi=100)
ax4=plt.axes([0.18, 0.18, 0.64, 0.75])
ax4.grid(which='major', axis='x', linewidth=0.75, linestyle='-', color='0.75')
ax4.grid(which='minor', axis='x', linewidth=0.25, linestyle='-', color='0.75')
ax4.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.75')
ax4.grid(which='minor', axis='y', linewidth=0.25, linestyle='-', color='0.75')
ax4.yaxis.set_major_locator(plt.MultipleLocator(500.0))
ax4.yaxis.set_minor_locator(plt.MultipleLocator(100.0))
ax4.xaxis.set_major_locator(plt.MultipleLocator(2.0))
ax4.xaxis.set_minor_locator(plt.MultipleLocator(0.5))
ax4.set_ylabel('Height z [m]')
ax4.set_xlabel('Velocity components [m/s]')

lw=2
ax4.plot(u_SRS,z_SRS,color='k', linewidth=lw, linestyle='-',label="SRS Ref: u ")
ax4.plot(v_SRS,z_SRS,color=colors[0], linewidth=lw, linestyle='-',label="SRS Ref: v")
ax4.plot(u_RANS,z_RANS,color=colors[1], linewidth=lw, linestyle='-',label="RANS Ref: u ")
ax4.plot(v_RANS,z_RANS,color=colors[3], linewidth=lw, linestyle='-',label="RANS Ref: v")
ax4.plot(ref_data[:,1],ref_data[:,0],color='k', marker='x',linewidth=lw, linestyle='none',label="Exp. Ref. u")
ax4.plot(ref_data[:,2],ref_data[:,0],color=colors[0], marker='x',linewidth=lw, linestyle='none',label="Exp. Ref. v")
if len(sys.argv) > 1:
    ax4.plot(u,z,color=colors[6], linewidth=lw, linestyle='-',label="SRS New: u ")
    ax4.plot(v,z,color=colors[7], linewidth=lw, linestyle='-',label="SRS New: v")

ax4.set_ylim(0,z_RANS[-1])
ax4.legend(fontsize=14,loc=(0.42,0.5))

savestring='fig_velocity_profiles.png'
fig.savefig(savestring, dpi=200)