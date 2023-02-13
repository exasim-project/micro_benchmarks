#!/usr/bin/env python3
"""
Description:
------------
This is a pvpython file that contains a collection of little functions for
paraview macros with i.a. default settings for renderviews.

Functionality:
--------------
This file can be loaded as a python module in paraview macros.

Script developer : Louis Fliessbach (louis.fliessbach@upstream-cfd.com)

Last updated : 10.01.2023
"""
import numpy as np
#### import the simple module from the paraview
from paraview.simple import *
from paraview import servermanager as sm

def ResetSession():
    print('\n    Reset paraview session\n')
    pxm = sm.ProxyManager()
    pxm.UnRegisterProxies()
    del pxm
    Disconnect()
    Connect()

def rescaleLUT(RGBPoints: list,PWFPoints: list,cbLimits: list):
    nPoints         = int(len(RGBPoints)/4)
    RGBPoints       = np.array(RGBPoints).reshape([nPoints,4])
    newPoints       = np.linspace(cbLimits[0],cbLimits[1],nPoints)
    RGBPoints[:,0]  = newPoints
    
    PWFPoints[0]    = cbLimits[0]
    PWFPoints[4]    = cbLimits[1]
    
    return list(RGBPoints.flatten()), PWFPoints

def getpvLUT(arrName,renderView,RGBPoints: list,ColorSpace:str,PWFPoints: list):
    # get color transfer function/color map for 'U'
    LUT = GetColorTransferFunction(arrName)
    LUT.AutomaticRescaleRangeMode = 'Never'
    LUT.RGBPoints = RGBPoints
    LUT.ColorSpace = ColorSpace
    LUT.ScalarRangeInitialized = 1.0
    LUT.NumberOfTableValues = 31
    
    # get color legend/bar for uLUT in view renderView1
    LUTColorBar = GetScalarBar(LUT, renderView)
    LUTColorBar.WindowLocation = 'UpperLeftCorner'
    LUTColorBar.Title = arrName
    LUTColorBar.AutoOrient = 1
    LUTColorBar.ComponentTitle = ''
    LUTColorBar.TitleColor = [0.0, 0.0, 0.0]
    LUTColorBar.TitleBold = 1
    LUTColorBar.TitleFontSize = 30
    LUTColorBar.LabelColor = [0.0, 0.0, 0.0]
    LUTColorBar.LabelBold = 1
    LUTColorBar.LabelFontSize = 20
    LUTColorBar.LabelFormat = '%-#.1e'
    LUTColorBar.RangeLabelFormat = '%-#.1e'
    LUTColorBar.ScalarBarThickness = 30
    LUTColorBar.ScalarBarLength = 0.35
    # set color bar visibility
    LUTColorBar.Visibility = 0
    
    # get opacity transfer function/opacity map for arrName
    PWF = GetOpacityTransferFunction(arrName)
    PWF.Points = PWFPoints
    PWF.ScalarRangeInitialized = 1
    
    return LUT, LUTColorBar, PWF

def getpvRenederView():
    # Create a new 'Render View'
    renderView1 = CreateView('RenderView')
    renderView1.ViewSize = [1920, 1080]
    renderView1.AxesGrid = 'GridAxes3DActor'
    renderView1.CenterOfRotation = [0.5104000568389893, 0.0, 0.18969473242759705]
    renderView1.StereoType = 'Crystal Eyes'
    renderView1.CameraPosition = [-12.296394675329045, -15.185213346721447, 8.73269576379674]
    renderView1.CameraFocalPoint = [0.49163477225458263, -0.02097466870686134, 0.12486586142872962]
    renderView1.CameraViewUp = [0.21284686862928617, 0.34039365087809187, 0.9158757410023431]
    renderView1.CameraFocalDisk = 1.0
    renderView1.CameraParallelScale = 0.6875215457208691
    renderView1.CameraParallelProjection = 1
    renderView1.Background = [1.0, 1.0, 1.0]
    renderView1.OrientationAxesLabelColor = [0.0, 0.0, 0.0]
    return renderView1

def getpvDisplay(inputFilter,renderView,arrName:str,arrLUT:list,arrPWF:list):
    # show data from extractBlock_Floor
    display = Show(inputFilter, renderView, 'UnstructuredGridRepresentation')
    # trace defaults for the display properties.
    display.Representation              = 'Surface'
    display.ColorArrayName              = ['POINTS', arrName]
    if arrLUT:
        display.LookupTable                 = arrLUT
    display.Ambient                     = 0.25
    display.DataAxesGrid                = 'GridAxesRepresentation'
    display.PolarAxes                   = 'PolarAxesRepresentation'
    if arrPWF:
        display.ScalarOpacityFunction       = arrPWF
    display.ScalarOpacityUnitDistance   = 0.21445263393639472
    display.ExtractedBlockIndex         = 1
    return display

def getpvSlice(inputFilter):
    slice1 = Slice(Input=inputFilter)
    slice1.SliceType = 'Plane'
    slice1.HyperTreeGridSlicer = 'Plane'
    slice1.Crinkleslice = 1
    slice1.SliceOffsetValues = [0.0]
    # init the 'Plane' selected for 'HyperTreeGridSlicer'
    slice1.HyperTreeGridSlicer.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]
    return slice1