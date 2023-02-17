#!/usr/bin/env python3
# Macro based on state file generated using paraview version 5.8.1
"""
Description:
------------
This is a pvpython script/macro to create image of slices coloured by different values

Functionality:
--------------
The script creates the following plots:
    - y-slice coloured by U, Cp, vorticity, nut, Co
Using the script:
    - run with pvbatch or pvpython
      'pvpython WindsorBody-Ensight_Slices.py <pathToRunDiretory>'
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
                    'Cp'                : [-1, 1],
                    'CpMean'            : [-1, 1],
                    'UNorm'             : [-1.2, 1.2],
                    'UMeanNorm'         : [-1.2, 1.2],
                    'vorticityNorm'     : [0, 50],
                    'nutNorm'           : [0, 200],
                    'nutMeanNorm'       : [0, 200],
                    'Co'                : [0, 1]
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
nuref           = caseDefDict['nu']
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
renderView1.CenterOfRotation            = [0.51, 0.0, 0.66]
renderView1.CameraPosition              = [0.62, -21.46, 0.66]
renderView1.CameraFocalPoint            = [0.62, 0.0, 0.66]
renderView1.CameraViewUp                = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale         = 0.665
renderView1.ViewSize                    = [3840, 1080]

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
case.CellArrays = ['Co', 'U', 'UMean', 'nut', 'nutMean', 'p', 'pMean', 'vorticity']

# create a new 'Cell Data to Point Data'
cellDatatoPointData1 = CellDatatoPointData(Input=case)
cellDatatoPointData1.CellDataArraytoprocess = ['Co', 'U', 'UMean', 'nut', 'nutMean', 'p', 'pMean', 'vorticity']
cellDatatoPointData1.PassCellData = 1

# Calulate additional arrays
calculator_UNorm = Calculator(Input=cellDatatoPointData1)
calculator_UNorm.ResultArrayName = 'UNorm'
calculator_UNorm.Function = 'U/%.4f'%(Uref)

# create a new 'Calculator'
calculator_UMeanNorm = Calculator(Input=calculator_UNorm)
calculator_UMeanNorm.ResultArrayName = 'UMeanNorm'
calculator_UMeanNorm.Function = 'UMean/%.4f'%(Uref)

# create a new 'Calculator'
calculator_vorticityNorm = Calculator(Input=calculator_UMeanNorm)
calculator_vorticityNorm.ResultArrayName = 'vorticityNorm'
calculator_vorticityNorm.Function = 'vorticity*%.4f/%.4f'%(lref,Uref)

# create a new 'Calculator'
calculator_nutNorm = Calculator(Input=calculator_vorticityNorm)
calculator_nutNorm.ResultArrayName = 'nutNorm'
calculator_nutNorm.Function = 'nut/%.2e'%(nuref)

# create a new 'Calculator'
calculator_nutMeanNorm = Calculator(Input=calculator_nutNorm)
calculator_nutMeanNorm.ResultArrayName = 'nutMeanNorm'
calculator_nutMeanNorm.Function = 'nutMean/%.2e'%(nuref)

# create a new 'Calculator'
calculator_Cp = Calculator(Input=calculator_nutMeanNorm)
calculator_Cp.ResultArrayName = 'Cp'
calculator_Cp.Function = '2*(p-0)/%.4f^2'%(Uref)

# create a new 'Calculator'
calculator_CpMean = Calculator(Input=calculator_Cp)
calculator_CpMean.ResultArrayName = 'CpMean'
calculator_CpMean.Function = '2*(pMean-0)/%.4f^2'%(Uref)


# extract geoemtry patches
extractBlock_Floor = ExtractBlock(Input=calculator_CpMean)
extractBlock_Floor.BlockIndices = [5]

extractBlock_WindsorComplete = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorComplete.BlockIndices = [10, 2, 9]

extractBlock_WindsorBase = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorBase.BlockIndices = [10]

# create Slice - x-normal at x = 0.63
slice_xNormal0p63 = pvsl.getpvSlice(inputFilter=calculator_CpMean)
slice_xNormal0p63.SliceType.Origin = [0.63, 0.0, 0.6600000262260437]
slice_xNormal0p63.SliceType.Normal = [1.0, 0.0, 0.0]

# create Slice - x-normal at x = 0.922
slice_xNormal0p922 = pvsl.getpvSlice(inputFilter=calculator_CpMean)
slice_xNormal0p922.SliceType.Origin = [0.922, 0.0, 0.6600000262260437]
slice_xNormal0p922.SliceType.Normal = [1.0, 0.0, 0.0]

# create Slice - y-normal at y = 0.0
slice_yNormal0p0 = pvsl.getpvSlice(inputFilter=calculator_CpMean)
slice_yNormal0p0.SliceType.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]
slice_yNormal0p0.SliceType.Normal = [0.0, 1.0, 0.0]

# create Slice - z-normal at z = 0.194
slice_zNormal0p194 = pvsl.getpvSlice(inputFilter=calculator_CpMean)
slice_zNormal0p194.SliceType.Origin = [0.5104000568389893, 0.0, 0.194]
slice_zNormal0p194.SliceType.Normal = [0.0, 0.0, 1.0]

#%%
# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------
# create colorbar an dLUT for all arrays shown in renderView1
LUT = {}; LUTColorBar = {}; PWF = {}
for arrName in cbLimits.keys():
    # rescale colorbar LUT
#    RGBPoints, PWFPoints            = pvsl.rescaleLUT(colouring[arrName]['RGBPoints'], colouring[arrName]['PWFPoints'], cbLimits[arrName])
#    LUT[arrName], LUTColorBar[arrName], PWF[arrName]     = pvsl.getpvLUT(arrName, renderView1, RGBPoints=RGBPoints,ColorSpace=colouring[arrName]['ColorSpace'],PWFPoints=PWFPoints)
    LUT[arrName], LUTColorBar[arrName], PWF[arrName]     = pvsl.getpvLUT(arrName, renderView1, RGBPoints=colouring[arrName]['RGBPoints'],ColorSpace=colouring[arrName]['ColorSpace'],PWFPoints=colouring[arrName]['PWFPoints'])
    LUT[arrName].RescaleTransferFunction(cbLimits[arrName][0], cbLimits[arrName][1])
    PWF[arrName].RescaleTransferFunction(cbLimits[arrName][0], cbLimits[arrName][1])
    LUTColorBar[arrName].Title             = """%s"""%(colouring[arrName]['cbTitle'])
    LUTColorBar[arrName].Visibility        = 0
        

LUT['UNorm'].VectorMode             = 'Component'

# trace defaults for the display properties.
extractBlock_WindsorCompleteDisplay         = pvsl.getpvDisplay(extractBlock_WindsorComplete,renderView1,arrName='',arrLUT=[],arrPWF=[])
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_WindsorCompleteDisplay.ScaleTransferFunction.Points = [-1.5624505615234374, 0.0, 0.5, 0.0, 1.044361801147461, 1.0, 0.5, 0.0]
# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_WindsorCompleteDisplay.OpacityTransferFunction.Points = [-1.5624505615234374, 0.0, 0.5, 0.0, 1.044361801147461, 1.0, 0.5, 0.0]
# change solid color
extractBlock_WindsorCompleteDisplay.AmbientColor = [0.6549019607843137, 0.6549019607843137, 0.6549019607843137]
extractBlock_WindsorCompleteDisplay.DiffuseColor = [0.6549019607843137, 0.6549019607843137, 0.6549019607843137]

## trace defaults for the display properties.
#extractBlock_FloorDisplay     = pvsl.getpvDisplay(extractBlock_Floor,renderView1,arrName='Cp',arrLUT=cpLUT,arrPWF=cfPWF)
## init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
#extractBlock_FloorDisplay.ScaleTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]
## init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
#extractBlock_FloorDisplay.OpacityTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]

# trace defaults for the display properties.
slice_yNormal0p0Display     = pvsl.getpvDisplay(slice_yNormal0p0,renderView1,arrName='UNorm',arrLUT=LUT['UNorm'],arrPWF=PWF['UNorm'])
# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_yNormal0p0Display.ScaleTransferFunction.Points = [205.84942626953125, 0.0, 0.5, 0.0, 33916.17578125, 1.0, 0.5, 0.0]
# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_yNormal0p0Display.OpacityTransferFunction.Points = [205.84942626953125, 0.0, 0.5, 0.0, 33916.17578125, 1.0, 0.5, 0.0]

for arrName in cbLimits.keys():
    if not arrName=='Co':
        slice_yNormal0p0Display.ColorArrayName              = ['POINTS', arrName]
    else:
        slice_yNormal0p0Display.ColorArrayName              = ['CELLS', arrName]
    slice_yNormal0p0Display.LookupTable                 = LUT[arrName]
    slice_yNormal0p0Display.ScalarOpacityFunction       = PWF[arrName]
    if colorBar:
        LUTColorBar[arrName].Visibility        = 1
    # ---- save images
    fName       = 'fig_Windsor_ySlice-y0p0_%s.png'%(arrName)
    SaveScreenshot(os.path.join(imageDir,fName), renderView1, ImageResolution=[5120, 1440])
    
    LUTColorBar[arrName].Visibility        = 0

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(calculator_UNorm)
# ----------------------------------------------------------------

#%% ---- save images
#fName       = 'fig_Windsor_isoQ-u.png'
#SaveScreenshot(os.path.join(imageDir,fName), renderView1, ImageResolution=[1920, 1080])

#pvsl.ResetSession