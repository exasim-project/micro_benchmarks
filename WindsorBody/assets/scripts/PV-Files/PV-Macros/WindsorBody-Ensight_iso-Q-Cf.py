#!/usr/bin/env python3
# Macro based on state file generated using paraview version 5.8.1
"""
Description:
------------
This is a pvpython script/macro to create an image of iso Q surfaces coloured by Ux

Functionality:
--------------
The script creates the following plots:
    - iso Q surfaces coloured by Ux with additional Cf contour on walls
Using the script:
    - run with pvbatch or pvpython
      'pvpython WindsorBody-Ensight_iso-Q-Cf.py <pathToRunDiretory>'
    - The script requires the simulation data in Ensight format

Script developer : Louis Fliessbach (louis.fliessbach@upstream-cfd.com)

Last updated : 10.01.2023
"""
# ---- import general python modules
import sys
import os
import glob
import json
import numpy as np

# ---- import the simple module from the paraview
sys.path.append('/share/software/ParaView/5.8.1-gnu7-openmpi3/lib64/python3.6/site-packages')       # only necessary, if script is started in an IDE like Spyder instead of pvpython (Change this to your local paraiew installation path)
from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()                                # disable automatic camera reset on 'Show'

# ---- import custom modules
import pvScriptLib as pvsl
# check command line arguments and get run directory or set it here
if len(sys.argv) > 1:
    runDir          = os.path.abspath(sys.argv[1])
else:
    runDir          = '../../../run_1'
sys.path.append(os.path.join(runDir,'scripts/python-files/'))
import IOFoamLib as io

# -----------------------------------------------------------------------------
# Start User input ############################################################
# -----------------------------------------------------------------------------
caseDirName     = runDir.split('/')[-1]
inputFile       = os.path.join(runDir,'EnSight/'+caseDirName+'.case')
rawDataDir      = 'postProcessing/'
imageDir        = os.path.join(runDir,'images')
if not os.path.exists(imageDir):
    os.makedirs(imageDir)

# load information about contour plot colouring for all arrays
with open(os.path.join(runDir,'scripts/PV-Files/PV-Macros/colouring.json'), 'r') as f:
    colouring = json.load(f)
# Switch, if colorbar is added or not
colorBar        = True
# set colobar limits
cbLimits        = {
                    'Cf' : [-0.01, 0.01],
                    'UNorm' : [-1.2, 1.2]
                  }
# -----------------------------------------------------------------------------
# End User input ##############################################################
# -----------------------------------------------------------------------------

#%%
# -----------------------------------------------------------------------------
# Load simulation data for normailisation
# ----------------------------------------------------------------------------- 
# load information from caseDefinition file in dictionary
caseDefDict     = io.get_caseDefinition(os.path.join(runDir,'system/include/caseDefinition'))

Aref            = caseDefDict['Aref']
lref            = caseDefDict['lref']
yawAngle        = caseDefDict['yawAngle']
Uinf            = caseDefDict['UinfMag']
timeStepSize    = caseDefDict['dt']
tAvg            = caseDefDict['tAvg']
tEnd            = caseDefDict['tEnd']

# get refrence value for U and p from reference probe
# If statements are only for developing status of the case
fileInP         = glob.glob(os.path.join(runDir,rawDataDir,'probes_reference','*','p'))
fileInU         = glob.glob(os.path.join(runDir,rawDataDir,'probes_reference','*','U'))
if len(fileInP) > 0:
    data            = io.mergeOFTimeSeries(fileInP)
    tFull           = data[:,0]
    dt              = tFull[1]-tFull[0]
    # tStepsSkip      = int(round(tAvg/dt))
    tStepsSkip      = np.where(tFull>=tAvg)[0][0]
    pref            = np.mean(data[tStepsSkip:,1])
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

#%%
renderView1     = pvsl.getpvRenederView()

# set camera placement for renderView1
renderView1.CameraPosition              = [-12.296394675329045, -15.185213346721447, 8.73269576379674]
renderView1.CameraFocalPoint            = [0.49163477225458263, -0.02097466870686134, 0.12486586142872962]
renderView1.CameraParallelScale         = 0.6875215457208691

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'EnSight Reader'
case            = EnSightReader(CaseFileName=inputFile)
case.CellArrays = ['Q', 'U', 'wallShearStress']

# create a new 'Cell Data to Point Data'
cellDatatoPointData1 = CellDatatoPointData(Input=case)
cellDatatoPointData1.CellDataArraytoprocess = ['Q', 'U', 'wallShearStress']

# Calulate additional arrays
calculator_UNorm = Calculator(Input=cellDatatoPointData1)
calculator_UNorm.ResultArrayName = 'UNorm'
calculator_UNorm.Function = 'U/%.4f'%(Uref)

calculator_Cf = Calculator(Input=calculator_UNorm)
calculator_Cf.ResultArrayName = 'Cf'
calculator_Cf.Function = '2*wallShearStress/%.4f^2'%(Uref)

calculator_QNorm = Calculator(Input=calculator_Cf)
calculator_QNorm.ResultArrayName = 'Q_norm'
calculator_QNorm.Function = 'Q*%.4f^2/%.4f^2'%(lref,Uref)

# Create iso Q Contour
contour1 = Contour(Input=calculator_QNorm)
contour1.ContourBy = ['POINTS', 'Q_norm']
contour1.GenerateTriangles = 0
contour1.Isosurfaces = [20.0]
contour1.PointMergeMethod = 'Octree Binning'
contour1.GenerateTriangles = 1

# init the 'Octree Binning' selected for 'PointMergeMethod'
contour1.PointMergeMethod.Maxnumberofpointsperleaf = 32

# extract geoemtry patches
extractBlock_Floor = ExtractBlock(Input=calculator_Cf)
extractBlock_Floor.BlockIndices = [5]

extractBlock_WindsorComplete = ExtractBlock(Input=calculator_Cf)
extractBlock_WindsorComplete.BlockIndices = [10, 2, 9]


#%%
# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------
# create colorbar an dLUT for all arrays shown in renderView1
LUT = {}; LUTColorBar = {}; PWF = {}
for arrName in cbLimits.keys():
    # rescale colorbar LUT
    RGBPoints, PWFPoints            = pvsl.rescaleLUT(colouring[arrName]['RGBPoints'], colouring[arrName]['PWFPoints'], cbLimits[arrName])
    LUT[arrName], LUTColorBar[arrName], PWF[arrName]     = pvsl.getpvLUT(arrName, renderView1, RGBPoints=RGBPoints,ColorSpace=colouring[arrName]['ColorSpace'],PWFPoints=PWFPoints)
    LUT[arrName].NumberOfTableValues       = 256
    LUTColorBar[arrName].Title             = """%s"""%(colouring[arrName]['cbTitle'])
    if colorBar:
        LUTColorBar[arrName].Visibility        = 1
    
LUTColorBar['Cf'].WindowLocation    = 'LowerRightCorner'
LUTColorBar['Cf'].TextPosition      = 'Ticks left/bottom, annotations right/top'
if colorBar:
    LUTColorBar['Cf'].Visibility        = 1

LUT['UNorm'].VectorMode             = 'Component'
    
# trace defaults for the display properties.
extractBlock_WindsorCompleteDisplay         = pvsl.getpvDisplay(extractBlock_WindsorComplete,renderView1,arrName='Cf',arrLUT=LUT['Cf'],arrPWF=PWF['Cf'])
extractBlock_WindsorCompleteDisplay.Opacity = 0.5
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_WindsorCompleteDisplay.ScaleTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]
# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_WindsorCompleteDisplay.OpacityTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# trace defaults for the display properties.
extractBlock_FloorDisplay     = pvsl.getpvDisplay(extractBlock_Floor,renderView1,arrName='Cf',arrLUT=LUT['Cf'],arrPWF=PWF['Cf'])
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_FloorDisplay.ScaleTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]
# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_FloorDisplay.OpacityTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]

## trace defaults for the display properties.
contour1Display     = pvsl.getpvDisplay(contour1,renderView1,arrName='UNorm',arrLUT=LUT['UNorm'],arrPWF=PWF['UNorm'])
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
contour1Display.ScaleTransferFunction.Points = [100.0, 0.0, 0.5, 0.0, 100.015625, 1.0, 0.5, 0.0]
# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
contour1Display.OpacityTransferFunction.Points = [100.0, 0.0, 0.5, 0.0, 100.015625, 1.0, 0.5, 0.0]

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(calculator_UNorm)
# ----------------------------------------------------------------

#%% ---- save images
fName       = 'fig_Windsor_isoQ-u.png'
SaveScreenshot(os.path.join(imageDir,fName), renderView1, ImageResolution=[2560, 1440])

pvsl.ResetSession