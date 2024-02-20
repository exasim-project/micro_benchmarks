#!/usr/bin/env python3

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
    x=tmp[:,0]
    y=tmp[:,1]
    p_rgh=tmp[:,3]
    wSS_x=tmp[:,4]
    wSS_y=tmp[:,5]
    wSS_z=tmp[:,5]
    return x,y,p_rgh,wSS_x,wSS_y,wSS_z

if len(sys.argv) > 1:
    # Set path to log file
    path=os.getcwd() + '/' + sys.argv[1]
    # Load SRS sample line
    x,y,p_rgh,wSS_x,wSS_y,wSS_z=loadprobes_perf_coeffs(path)
    l=np.sqrt(np.power(x-x[0],2)+np.power(y-y[0],2))                       # Create distance array
    magwSS=np.sqrt(np.power(wSS_x,2)+np.power(wSS_y,2)+np.power(wSS_z,2))  # Wallshearstress magnitude

# Load RANS reference data
rans_data=np.loadtxt("Leipzig_SST_RANS_p_wSS_Ref.dat",comments='#')
l_RANS=np.sqrt(np.power(rans_data[:,0]-rans_data[:,0][0],2)+np.power(rans_data[:,1]-rans_data[:,1][0],2))
magwSS_RANS=np.sqrt(np.power(rans_data[:,2],2)+np.power(rans_data[:,3],2)+np.power(rans_data[:,4],2))

# Load SRS reference data
x_SRS,y_SRS,p_rgh_SRS,wSS_x_SRS,wSS_y_SRS,wSS_z_SRS=loadprobes_perf_coeffs("Leipzig_SST_SRS_pprime_wSS_Ref.dat")
srs_data=np.loadtxt("Leipzig_SST_SRS_pprime_wSS_Ref.dat",comments='#')
l_SRS=np.sqrt(np.power(x_SRS-x_SRS[0],2)+np.power(y_SRS-y_SRS[0],2))
magwSS_SRS=np.sqrt(np.power(wSS_x_SRS,2)+np.power(wSS_y_SRS,2)+np.power(wSS_z_SRS,2))

plt.rcParams.update({'font.size': 20})
fig=plt.figure(num=0,figsize=(8.0,6.0), dpi=100)
ax4=plt.axes([0.18, 0.18, 0.64, 0.75])
ax4.grid(which='major', axis='x', linewidth=0.75, linestyle='-', color='0.75')
ax4.grid(which='minor', axis='x', linewidth=0.25, linestyle='-', color='0.75')
ax4.grid(which='major', axis='y', linewidth=0.75, linestyle='-', color='0.75')
ax4.grid(which='minor', axis='y', linewidth=0.25, linestyle='-', color='0.75')
ax4.yaxis.set_major_locator(plt.MultipleLocator(0.05))
ax4.yaxis.set_minor_locator(plt.MultipleLocator(0.01))
ax4.xaxis.set_major_locator(plt.MultipleLocator(1.0))
ax4.xaxis.set_minor_locator(plt.MultipleLocator(0.2))
ax4.set_xlabel('Length l [km]')
ax4.set_ylabel(r'$1+\frac{\tau_{SRS}-\tau_{RANS}}{\tau_{RANS}}$')

h1,=ax4.plot(0.001*l_SRS,1+np.divide(magwSS_SRS-magwSS_RANS,magwSS_RANS),color=colors[0], linewidth=2, linestyle='-.')
if len(sys.argv) > 1:
    h2,=ax4.plot(0.001*l,1+np.divide(magwSS-magwSS_RANS,magwSS_RANS),color=colors[0], linewidth=2, linestyle='-')
    ax4.legend([h1,h2],["Dash-dot: Ref. SRS","Solid: New SRS"],fontsize=14,loc=(0.42,0.8))
ax4.hlines(y = 1, xmin = 0, xmax = 0.001*l_RANS[-1],color='k', linewidth=1, linestyle='-')
ax4.yaxis.label.set_color(colors[0])
ax4.set_xlim(0,0.001*l_RANS[-1])
ax4.set_ylim(0.9,1.1)

ax5 = ax4.twinx()
ax5.plot(0.001*l_SRS,np.sqrt(p_rgh_SRS),color=colors[1], linewidth=2, linestyle='-.')
if len(sys.argv) > 1:
    ax5.plot(0.001*l,np.sqrt(p_rgh),color=colors[1], linewidth=2, linestyle='-')
ax5.set_ylabel(r'$p_{rgh}^{RMS}$')
ax5.yaxis.label.set_color(colors[1])

savestring='fig_STG_recovery.png'
fig.savefig(savestring, dpi=200)