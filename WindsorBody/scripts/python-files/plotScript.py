#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import re
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import IOFoamLib as io

# check command line arguments and get run directory or set it here
if len(sys.argv) > 1:
    runDir          = os.path.abspath(sys.argv[1])
else:
    runDir          = '../../run_1'


rawDataDir      = 'postProcessing'

# load information from caseDefinition file in dictionary
caseDefDict     = io.get_caseDefinition(os.path.join(runDir,'system/include'),'caseDefinition')

Aref            = caseDefDict['Aref']
lref            = caseDefDict['lref']
yawAngle        = caseDefDict['yawAngle']
Uinf            = caseDefDict['UinfMag']
timeStepSize    = caseDefDict['dt']
tAvg            = caseDefDict['tAvg']
tEnd            = caseDefDict['tEnd']

# set and create image directory
imageDir        = 'images'
imageDirPath    = os.path.join(runDir,imageDir)
if not os.path.exists(imageDirPath):
    os.makedirs(imageDirPath)

# set plot settings
figSize         = [7.5,5]    # in cm 
cm2inch         = lambda cm : cm/2.54
DPI             = 300

#%% reference point
# get refrence value for U and p from reference probe
# If statements are only for developing status of the case
fileInP         = glob.glob(os.path.join(runDir,rawDataDir,'probes_reference','*','p'))
fileInCp        = glob.glob(os.path.join(runDir,rawDataDir,'probes_reference','*','cp'))
fileInU         = glob.glob(os.path.join(runDir,rawDataDir,'probes_reference','*','U'))
if len(fileInP) > 0:
    data            = io.mergeOFTimeSeries(fileInP)
    tFull           = data[:,0]
    dt              = tFull[1]-tFull[0]
    # tStepsSkip      = int(round(tAvg/dt))
    tStepsSkip      = np.where(tFull>=tAvg)[0][0]
    pref            = np.mean(data[tStepsSkip:,1])
elif len(fileInCp) > 0:
    data            = io.mergeOFTimeSeries(fileInCp)
    tFull           = data[:,0]
    dt              = tFull[1]-tFull[0]
    # tStepsSkip      = int(round(tAvg/dt))
    tStepsSkip      = np.where(tFull>=tAvg)[0][0]
    pref            = np.mean(data[tStepsSkip:,1])*Uinf**2/2
else:
    pref            = 23.5089

if len(fileInU) > 0:
    data            = io.mergeOFTimeSeries(fileInU)
    tFull           = data[:,0]
    dt              = tFull[1]-tFull[0]
    # tStepsSkip      = int(round(tAvg/dt))
    tStepsSkip      = np.where(tFull>=tAvg)[0][0]
    Uref            = np.mean(data[tStepsSkip:,1])
else:
    Uref            = 40.1697

print('pref: %8.4f\nUref:%8.4f'%(pref, Uref))

#%% force coefficients
# reference value from experimentel data (Max Varney, Giancarlo Pavia, Martin Passmore, Conor Crickmore: https://repository.lboro.ac.uk/articles/dataset/Windsor_Body_Experimental_Aerodynamic_Dataset/13161284)
Cd_ref          = 0.3298
Cl_ref          = -0.0382
Cs_ref          = 0.1509
Cmp_ref         = -0.0259
Cmy_ref         = 0.0322
Cmr_ref         = 0.0424
# load transient data from raw OF files
fileIn          = glob.glob(os.path.join(runDir,rawDataDir,'forceCoeffsAll','*','coefficient.dat'))
data            = io.mergeOFTimeSeries(fileIn)
tFull           = data[:,0]
dt              = tFull[1]-tFull[0]
# tStepsSkip      = int(round(tAvg/dt))
tStepsSkip      = np.where(tFull>=tAvg)[0][0]
t               = data[tStepsSkip:,0]
coeffs          = data[tStepsSkip:,1:]*Uinf**2/Uref**2
coeffsMean      = np.mean(coeffs,axis=0)
coeffsFull      = data[:,1:]*Uinf**2/Uref**2

# plot Cd time series
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tFull,coeffsFull[:,0],'k-',label='transient')
ax.plot([-100,100],[coeffsMean[0],coeffsMean[0]],'r--',label='mean')
ax.plot([-100,100],[Cd_ref,Cd_ref],':',color='grey',label='Exp. Varney et al.')
ax.set_xlabel('time in s')
ax.set_ylabel(r'$C_\mathrm{d}$')
ax.set_xlim([np.min(tFull),np.max(tFull)])
ax.set_ylim([0.2,0.4])
ax.legend()
outFile         = os.path.join(imageDirPath,'Cd_t.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# plot Cl time series
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tFull,coeffsFull[:,3],'k-',label='transient')
ax.plot([-100,100],[coeffsMean[3],coeffsMean[3]],'r--',label='mean')
ax.plot([-100,100],[Cl_ref,Cl_ref],':',color='grey',label='Exp. Varney et al.')
ax.set_xlabel('time in s')
ax.set_ylabel(r'$C_\mathrm{l}$')
ax.set_xlim([np.min(tFull),np.max(tFull)])
ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'Cl_t.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# plot Cs time series
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tFull,coeffsFull[:,9],'k-',label='transient')
ax.plot([-100,100],[coeffsMean[9],coeffsMean[9]],'r--',label='mean')
ax.plot([-100,100],[Cs_ref,Cs_ref],':',color='grey',label='Exp. Varney et al.')
ax.set_xlabel('time in s')
ax.set_ylabel(r'$C_\mathrm{s}$')
ax.set_xlim([np.min(tFull),np.max(tFull)])
ax.set_ylim([0.1,0.2])
ax.legend()
outFile         = os.path.join(imageDirPath,'Cs_t.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# plot Cm_pitch time series
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tFull,coeffsFull[:,6],'k-',label='transient')
ax.plot([-100,100],[coeffsMean[6],coeffsMean[6]],'r--',label='mean')
ax.plot([-100,100],[Cmp_ref,Cmp_ref],':',color='grey',label='Exp. Varney et al.')
ax.set_xlabel('time in s')
ax.set_ylabel(r'$C_\mathrm{m_{Pitch}}$')
ax.set_xlim([np.min(tFull),np.max(tFull)])
ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'Cmpitch_t.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# # plot Cm_roll time series
# fig             = plt.figure()
# fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
# ax              = fig.add_subplot(1, 1, 1)
# ax.plot(tFull,-coeffsFull[:,7],'k-',label='transient')
# ax.plot([-100,100],[-coeffsMean[7],-coeffsMean[7]],'r--',label='mean')
# ax.plot([-100,100],[Cmr_ref,Cmr_ref],':',color='grey',label='Exp. Varney et al.')
# ax.set_xlabel('time in s')
# ax.set_ylabel(r'$C_\mathrm{m_{Roll}}$')
# ax.set_xlim([np.min(tFull),np.max(tFull)])
# ax.set_ylim([0,0.1])
# ax.legend()
# outFile         = os.path.join(imageDirPath,'Cmroll_t.png')
# fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# # plot Cm_yaw time series
# fig             = plt.figure()
# fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
# ax              = fig.add_subplot(1, 1, 1)
# ax.plot(tFull,-coeffsFull[:,8],'k-',label='transient')
# ax.plot([-100,100],[-coeffsMean[8],-coeffsMean[8]],'r--',label='mean')
# ax.plot([-100,100],[Cmy_ref,Cmy_ref],':',color='grey',label='Exp. Varney et al.')
# ax.set_xlabel('time in s')
# ax.set_ylabel(r'$C_\mathrm{m_{Yaw}}$')
# ax.set_xlim([np.min(tFull),np.max(tFull)])
# ax.set_ylim([0,0.1])
# ax.legend()
# outFile         = os.path.join(imageDirPath,'Cmyaw_t.png')
# fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

#%% pressure tab probes
# load reference data  (Max Varney, Giancarlo Pavia, Martin Passmore, Conor Crickmore: https://repository.lboro.ac.uk/articles/dataset/Windsor_Body_Experimental_Aerodynamic_Dataset/13161284)
inFile          = os.path.join(runDir,'../ExpData_LoughboroughUniv_VarneyEtAl/SetB-YawedFlow/Pressure_Mean/SquareBack_Pressure_Tapping_Map.csv')
tabLocations    = io.load_data(inFile,',',Unpack=False)
inFile          = os.path.join(runDir,'../ExpData_LoughboroughUniv_VarneyEtAl/SetB-YawedFlow/Pressure_Mean/SquareBack_NW_2_5yaw_Pressures_Averages_Mean.csv')
CpMeanRef       = io.load_data(inFile,',',Unpack=False)
inFile          = os.path.join(runDir,'../ExpData_LoughboroughUniv_VarneyEtAl/SetB-YawedFlow/Pressure_Mean/SquareBack_NW_2_5yaw_Pressures_Averages_RMS.csv')
CpRMSRef        = io.load_data(inFile,',',Unpack=False)

CenterlineIdx   = np.where(tabLocations[:,3]==1)[0]
GlasshouseIdx   = np.where(tabLocations[:,3]==2)[0]
BumperIdx       = np.where(tabLocations[:,3]==3)[0]


# load transient data from raw OF files of centerline probes
fileIn          = glob.glob(os.path.join(runDir,rawDataDir,'probes_1-Centerline','*','cp'))
data            = io.mergeOFTimeSeries(fileIn)
tFull           = data[:,0]
dt              = tFull[1]-tFull[0]
# tStepsSkip      = int(round(tAvg/dt))
tStepsSkip      = np.where(tFull>=tAvg)[0][0]
t               = data[tStepsSkip:,0]
Cp              = (data[tStepsSkip:,1:]*Uinf**2-2*pref)/Uref**2
CpMean          = np.mean(Cp,axis=0)
CpRMS           = np.sqrt(np.mean((Cp-CpMean)**2,axis=0))
CpFull          = (data[tStepsSkip:,1:]*Uinf**2-2*pref)/Uref**2

# plot CpMean of centerline probes
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tabLocations[CenterlineIdx,0],CpMeanRef[CenterlineIdx],'k*',label='Exp. Varney et al.')
ax.plot(tabLocations[CenterlineIdx,0],CpMean,'r+',label='OF')
ax.set_xlabel('x in m')
ax.set_ylabel(r'Mean($C_p$)')
#ax.set_xlim([np.min(tFull),np.max(tFull)])
#ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'CpMean_Centerline-probes.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)
# plot CpRMS of centerline probes
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tabLocations[CenterlineIdx,0],CpRMSRef[CenterlineIdx],'k*',label='Exp. Varney et al.')
ax.plot(tabLocations[CenterlineIdx,0],CpRMS,'r+',label='OF')
ax.set_xlabel('x in m')
ax.set_ylabel(r'RMS($C_p$)')
#ax.set_xlim([np.min(tFull),np.max(tFull)])
#ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'CpRMS_Centerline-probes.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

# load transient data from raw OF files of upper glasshouse probes
fileIn          = glob.glob(os.path.join(runDir,rawDataDir,'probes_2-Glasshouse','*','cp'))
data            = io.mergeOFTimeSeries(fileIn)
tFull           = data[:,0]
dt              = tFull[1]-tFull[0]
# tStepsSkip      = int(round(tAvg/dt))
tStepsSkip      = np.where(tFull>=tAvg)[0][0]
t               = data[tStepsSkip:,0]
Cp              = (data[tStepsSkip:,1:]*Uinf**2-2*pref)/Uref**2
CpMean          = np.mean(Cp,axis=0)
CpRMS           = np.sqrt(np.mean((Cp-CpMean)**2,axis=0))
CpFull          = (data[tStepsSkip:,1:]*Uinf**2-2*pref)/Uref**2

# plot CpMean of centerline probes
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tabLocations[GlasshouseIdx,0],CpMeanRef[GlasshouseIdx],'k*',label='Exp. Varney et al.')
ax.plot(tabLocations[GlasshouseIdx,0],CpMean,'r+',label='OF')
ax.set_xlabel('x in m')
ax.set_ylabel(r'Mean($C_p$)')
#ax.set_xlim([np.min(tFull),np.max(tFull)])
#ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'CpMean_Glasshouse-probes.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)
# plot CpRMS of centerline probes
fig             = plt.figure()
fig.set_size_inches(cm2inch(figSize[0]), cm2inch(figSize[1]))
ax              = fig.add_subplot(1, 1, 1)
ax.plot(tabLocations[GlasshouseIdx,0],CpRMSRef[GlasshouseIdx],'k*',label='Exp. Varney et al.')
ax.plot(tabLocations[GlasshouseIdx,0],CpRMS,'r+',label='OF')
ax.set_xlabel('x in m')
ax.set_ylabel(r'RMS($C_p$)')
#ax.set_xlim([np.min(tFull),np.max(tFull)])
#ax.set_ylim([-0.2,0])
ax.legend()
outFile         = os.path.join(imageDirPath,'CpRMS_Glasshouse-probes.png')
fig.savefig(outFile,dpi=DPI, facecolor='w', edgecolor='w', orientation='portrait', bbox_inches='tight', pad_inches=0.1)

plt.close('all')
