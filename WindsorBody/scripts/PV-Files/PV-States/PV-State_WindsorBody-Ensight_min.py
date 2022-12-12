# state file generated using paraview version 5.8.1

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# trace generated using paraview version 5.8.1
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [1325, 814]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.CenterOfRotation = [0.5104000568389893, 0.0, 0.6232916081998637]
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [-10.119184527120522, -15.471319891137597, 11.671343585956672]
renderView1.CameraFocalPoint = [0.27694346199371106, -0.025756787285943914, 0.3732604576748269]
renderView1.CameraViewUp = [0.1947960929775598, 0.49028654101656777, 0.8495137372983954]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 0.6924363589995397
renderView1.CameraParallelProjection = 1
renderView1.Background = [1.0, 1.0, 1.0]

SetActiveView(None)

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
windsorBodycase = EnSightReader(CaseFileName='/work/fliessbach/run_OF/BMBF_2022_EXASIM/WP2_Microbenchmarks/WindsorBody/03_Solve/WindsorBody_OF-v2206_incomp_AutoCFD3g1_test01/EnSight/WindsorBody_OF-v2206_incomp_AutoCFD3g1_test01.case')
windsorBodycase.CellArrays = ['Co', 'Q', 'U', 'UMean', 'UPrime2Mean', 'cp', 'k', 'nut', 'nutMean', 'omega', 'p', 'pMean', 'pPrime2Mean', 'vorticity', 'wallShearStress', 'wallShearStressMean', 'yPlus']

# create a new 'Cell Data to Point Data'
cellDatatoPointData1 = CellDatatoPointData(Input=windsorBodycase)
cellDatatoPointData1.CellDataArraytoprocess = ['Co', 'Q', 'U', 'UMean', 'UPrime2Mean', 'cp', 'k', 'nut', 'nutMean', 'omega', 'p', 'pMean', 'pPrime2Mean', 'vorticity', 'wallShearStress', 'wallShearStressMean', 'yPlus']

# create a new 'Calculator'
calculator_UNorm = Calculator(Input=cellDatatoPointData1)
calculator_UNorm.ResultArrayName = 'U_norm'
calculator_UNorm.Function = 'U/40'

# create a new 'Calculator'
calculator_UMeanNorm = Calculator(Input=calculator_UNorm)
calculator_UMeanNorm.ResultArrayName = 'UMean_norm'
calculator_UMeanNorm.Function = 'UMean/40'

# create a new 'Calculator'
calculator_Cp = Calculator(Input=calculator_UMeanNorm)
calculator_Cp.ResultArrayName = 'Cp'
calculator_Cp.Function = '2*(p-0)/40^2'

# create a new 'Calculator'
calculator_CpMean = Calculator(Input=calculator_Cp)
calculator_CpMean.ResultArrayName = 'CpMean'
calculator_CpMean.Function = '2*(pMean-0)/40^2'

# create a new 'Calculator'
calculator_QNorm = Calculator(Input=calculator_CpMean)
calculator_QNorm.ResultArrayName = 'Q_norm'
calculator_QNorm.Function = 'Q*40^2/0.6375^2'

# create a new 'Contour'
contour1 = Contour(Input=calculator_QNorm)
contour1.ContourBy = ['POINTS', 'Q_norm']
contour1.Isosurfaces = [100.0]
contour1.PointMergeMethod = 'Octree Binning'

# init the 'Octree Binning' selected for 'PointMergeMethod'
contour1.PointMergeMethod.Maxnumberofpointsperleaf = 32

# create a new 'Extract Block'
extractBlock_Floor = ExtractBlock(Input=calculator_CpMean)
extractBlock_Floor.BlockIndices = [5]

# create a new 'Extract Block'
extractBlock_WindsorComplete = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorComplete.BlockIndices = [10, 2, 9]

# create a new 'Extract Block'
extractBlock_WindsorBase = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorBase.BlockIndices = [10]

# create a new 'Slice'
slice_Bumper = Slice(Input=extractBlock_WindsorComplete)
slice_Bumper.SliceType = 'Plane'
slice_Bumper.HyperTreeGridSlicer = 'Plane'
slice_Bumper.Triangulatetheslice = 0
slice_Bumper.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Bumper.SliceType.Origin = [-0.037624046206474304, 0.0006063580513000488, 0.1249]
slice_Bumper.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Bumper.HyperTreeGridSlicer.Origin = [-0.037624046206474304, 0.0006063580513000488, 0.16949999332427979]

# create a new 'Slice'
slice_Centerline = Slice(Input=extractBlock_WindsorComplete)
slice_Centerline.SliceType = 'Plane'
slice_Centerline.HyperTreeGridSlicer = 'Plane'
slice_Centerline.Triangulatetheslice = 0
slice_Centerline.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Centerline.SliceType.Normal = [0.043619387, 0.999048222, 0.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Centerline.HyperTreeGridSlicer.Origin = [-0.037624046206474304, 0.0006063580513000488, 0.16949999332427979]

# create a new 'Slice'
slice_Glasshouse = Slice(Input=extractBlock_WindsorComplete)
slice_Glasshouse.SliceType = 'Plane'
slice_Glasshouse.HyperTreeGridSlicer = 'Plane'
slice_Glasshouse.Triangulatetheslice = 0
slice_Glasshouse.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Glasshouse.SliceType.Origin = [-0.037624046206474304, 0.0006063580513000488, 0.2594]
slice_Glasshouse.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Glasshouse.HyperTreeGridSlicer.Origin = [-0.037624046206474304, 0.0006063580513000488, 0.16949999332427979]

# create a new 'Slice'
slice_xNormal0p922 = Slice(Input=calculator_CpMean)
slice_xNormal0p922.SliceType = 'Plane'
slice_xNormal0p922.HyperTreeGridSlicer = 'Plane'
slice_xNormal0p922.Crinkleslice = 1
slice_xNormal0p922.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_xNormal0p922.SliceType.Origin = [0.922, 0.0, 0.6600000262260437]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_xNormal0p922.HyperTreeGridSlicer.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]

# create a new 'Slice'
slice_xNormal0p63 = Slice(Input=calculator_CpMean)
slice_xNormal0p63.SliceType = 'Plane'
slice_xNormal0p63.HyperTreeGridSlicer = 'Plane'
slice_xNormal0p63.Crinkleslice = 1
slice_xNormal0p63.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_xNormal0p63.SliceType.Origin = [0.63, 0.0, 0.6600000262260437]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_xNormal0p63.HyperTreeGridSlicer.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]

# create a new 'Slice'
slice_zNormal0p194 = Slice(Input=calculator_CpMean)
slice_zNormal0p194.SliceType = 'Plane'
slice_zNormal0p194.HyperTreeGridSlicer = 'Plane'
slice_zNormal0p194.Crinkleslice = 1
slice_zNormal0p194.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_zNormal0p194.SliceType.Origin = [0.5104000568389893, 0.0, 0.194]
slice_zNormal0p194.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_zNormal0p194.HyperTreeGridSlicer.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]

# create a new 'Slice'
slice_yNormal0p0 = Slice(Input=calculator_CpMean)
slice_yNormal0p0.SliceType = 'Plane'
slice_yNormal0p0.HyperTreeGridSlicer = 'Plane'
slice_yNormal0p0.Crinkleslice = 1
slice_yNormal0p0.Triangulatetheslice = 0
slice_yNormal0p0.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_yNormal0p0.SliceType.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]
slice_yNormal0p0.SliceType.Normal = [0.0, 1.0, 0.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_yNormal0p0.HyperTreeGridSlicer.Origin = [0.5104000568389893, 0.0, 0.6600000262260437]

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from slice_yNormal0p0
slice_yNormal0p0Display = Show(slice_yNormal0p0, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'UMean_norm'
uMean_normLUT = GetColorTransferFunction('UMean_norm')
uMean_normLUT.AutomaticRescaleRangeMode = 'Never'
uMean_normLUT.RGBPoints = [-1.5, 0.404088, 0.131038, 0.592767, -1.311765, 0.486469, 0.230957, 0.651243, -1.1235300000000001, 0.575165, 0.339335, 0.717723, -0.9352935, 0.662741, 0.454332, 0.784263, -0.7470585000000001, 0.742071, 0.570213, 0.842918, -0.5588235, 0.806935, 0.678992, 0.886227, -0.3705885, 0.852219, 0.771315, 0.90763, -0.18235350000000006, 0.873345, 0.837327, 0.901572, 0.005882354999999784, 0.866783, 0.86682, 0.866745, 0.194118, 0.82839, 0.858225, 0.796812, 0.38235299999999994, 0.762578, 0.814287, 0.700202, 0.5705879999999999, 0.676429, 0.744229, 0.585735, 0.7588230000000005, 0.577033, 0.65732, 0.461526, 0.9470594999999999, 0.47128, 0.562476, 0.33476, 1.1352945, 0.365461, 0.467957, 0.21076, 1.3235295000000002, 0.264758, 0.381138, 0.0878313, 1.5, 0.182591, 0.312249, 0.0]
uMean_normLUT.ColorSpace = 'Lab'
uMean_normLUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
slice_yNormal0p0Display.Representation = 'Surface'
slice_yNormal0p0Display.ColorArrayName = ['POINTS', 'UMean_norm']
slice_yNormal0p0Display.LookupTable = uMean_normLUT
slice_yNormal0p0Display.Ambient = 1.0
slice_yNormal0p0Display.Diffuse = 0.0
slice_yNormal0p0Display.OSPRayScaleArray = 'Co'
slice_yNormal0p0Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_yNormal0p0Display.SelectOrientationVectors = 'U'
slice_yNormal0p0Display.ScaleFactor = 1.102080011367798
slice_yNormal0p0Display.SelectScaleArray = 'Co'
slice_yNormal0p0Display.GlyphType = 'Arrow'
slice_yNormal0p0Display.GlyphTableIndexArray = 'Co'
slice_yNormal0p0Display.GaussianRadius = 0.05510400056838989
slice_yNormal0p0Display.SetScaleArray = ['POINTS', 'Co']
slice_yNormal0p0Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_yNormal0p0Display.OpacityArray = ['POINTS', 'Co']
slice_yNormal0p0Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_yNormal0p0Display.DataAxesGrid = 'GridAxesRepresentation'
slice_yNormal0p0Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_yNormal0p0Display.ScaleTransferFunction.Points = [205.84942626953125, 0.0, 0.5, 0.0, 33916.17578125, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_yNormal0p0Display.OpacityTransferFunction.Points = [205.84942626953125, 0.0, 0.5, 0.0, 33916.17578125, 1.0, 0.5, 0.0]

# show data from extractBlock_WindsorComplete
extractBlock_WindsorCompleteDisplay = Show(extractBlock_WindsorComplete, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'wallShearStress'
wallShearStressLUT = GetColorTransferFunction('wallShearStress')
wallShearStressLUT.AutomaticRescaleRangeMode = 'Never'
wallShearStressLUT.RGBPoints = [-5.0, 0.0, 0.266667, 0.105882, -4.411765000000001, 0.062284, 0.386621, 0.170473, -3.7843149999999994, 0.15917, 0.516263, 0.251211, -3.156865, 0.314187, 0.649135, 0.354556, -2.529410000000001, 0.493195, 0.765398, 0.496655, -1.9019600000000003, 0.670588, 0.866897, 0.647059, -1.2745099999999998, 0.796078, 0.91857, 0.772549, -0.6470600000000006, 0.892503, 0.950865, 0.877278, -0.01960784999999987, 0.966321, 0.968089, 0.965859, 0.6078450000000002, 0.930488, 0.885198, 0.932872, 1.2352950000000007, 0.871742, 0.788005, 0.886736, 1.8627450000000003, 0.7807, 0.672357, 0.825221, 2.490195, 0.681968, 0.545175, 0.742561, 3.1176449999999996, 0.583852, 0.40692, 0.652134, 3.7451000000000008, 0.497732, 0.234679, 0.55371, 4.37255, 0.383852, 0.103345, 0.431911, 5.0, 0.25098, 0.0, 0.294118]
wallShearStressLUT.ColorSpace = 'Lab'
wallShearStressLUT.NanColor = [1.0, 0.0, 0.0]
wallShearStressLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'wallShearStress'
wallShearStressPWF = GetOpacityTransferFunction('wallShearStress')
wallShearStressPWF.Points = [-5.0, 0.0, 0.5, 0.0, 5.0, 1.0, 0.5, 0.0]
wallShearStressPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
extractBlock_WindsorCompleteDisplay.Representation = 'Surface'
extractBlock_WindsorCompleteDisplay.ColorArrayName = ['POINTS', 'wallShearStress']
extractBlock_WindsorCompleteDisplay.LookupTable = wallShearStressLUT
extractBlock_WindsorCompleteDisplay.Opacity = 0.5
extractBlock_WindsorCompleteDisplay.Ambient = 0.25
extractBlock_WindsorCompleteDisplay.OSPRayScaleArray = 'Co'
extractBlock_WindsorCompleteDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
extractBlock_WindsorCompleteDisplay.SelectOrientationVectors = 'U'
extractBlock_WindsorCompleteDisplay.ScaleFactor = 0.10577961504459382
extractBlock_WindsorCompleteDisplay.SelectScaleArray = 'Co'
extractBlock_WindsorCompleteDisplay.GlyphType = 'Arrow'
extractBlock_WindsorCompleteDisplay.GlyphTableIndexArray = 'Co'
extractBlock_WindsorCompleteDisplay.GaussianRadius = 0.00528898075222969
extractBlock_WindsorCompleteDisplay.SetScaleArray = ['POINTS', 'Co']
extractBlock_WindsorCompleteDisplay.ScaleTransferFunction = 'PiecewiseFunction'
extractBlock_WindsorCompleteDisplay.OpacityArray = ['POINTS', 'Co']
extractBlock_WindsorCompleteDisplay.OpacityTransferFunction = 'PiecewiseFunction'
extractBlock_WindsorCompleteDisplay.DataAxesGrid = 'GridAxesRepresentation'
extractBlock_WindsorCompleteDisplay.PolarAxes = 'PolarAxesRepresentation'
extractBlock_WindsorCompleteDisplay.ScalarOpacityFunction = wallShearStressPWF
extractBlock_WindsorCompleteDisplay.ScalarOpacityUnitDistance = 0.02820929837894948
extractBlock_WindsorCompleteDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_WindsorCompleteDisplay.ScaleTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_WindsorCompleteDisplay.OpacityTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# show data from extractBlock_Floor
extractBlock_FloorDisplay = Show(extractBlock_Floor, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
extractBlock_FloorDisplay.Representation = 'Surface'
extractBlock_FloorDisplay.ColorArrayName = ['POINTS', 'wallShearStress']
extractBlock_FloorDisplay.LookupTable = wallShearStressLUT
extractBlock_FloorDisplay.Ambient = 0.25
extractBlock_FloorDisplay.OSPRayScaleArray = 'Co'
extractBlock_FloorDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
extractBlock_FloorDisplay.SelectOrientationVectors = 'U'
extractBlock_FloorDisplay.ScaleFactor = 1.102080011367798
extractBlock_FloorDisplay.SelectScaleArray = 'Co'
extractBlock_FloorDisplay.GlyphType = 'Arrow'
extractBlock_FloorDisplay.GlyphTableIndexArray = 'Co'
extractBlock_FloorDisplay.GaussianRadius = 0.05510400056838989
extractBlock_FloorDisplay.SetScaleArray = ['POINTS', 'Co']
extractBlock_FloorDisplay.ScaleTransferFunction = 'PiecewiseFunction'
extractBlock_FloorDisplay.OpacityArray = ['POINTS', 'Co']
extractBlock_FloorDisplay.OpacityTransferFunction = 'PiecewiseFunction'
extractBlock_FloorDisplay.DataAxesGrid = 'GridAxesRepresentation'
extractBlock_FloorDisplay.PolarAxes = 'PolarAxesRepresentation'
extractBlock_FloorDisplay.ScalarOpacityFunction = wallShearStressPWF
extractBlock_FloorDisplay.ScalarOpacityUnitDistance = 0.21445263393639472
extractBlock_FloorDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_FloorDisplay.ScaleTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_FloorDisplay.OpacityTransferFunction.Points = [227.72463989257812, 0.0, 0.5, 0.0, 143207.8125, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for wallShearStressLUT in view renderView1
wallShearStressLUTColorBar = GetScalarBar(wallShearStressLUT, renderView1)
wallShearStressLUTColorBar.WindowLocation = 'UpperRightCorner'
wallShearStressLUTColorBar.Title = 'wallShearStress'
wallShearStressLUTColorBar.ComponentTitle = 'Magnitude'

# set color bar visibility
wallShearStressLUTColorBar.Visibility = 1

# get color legend/bar for uMean_normLUT in view renderView1
uMean_normLUTColorBar = GetScalarBar(uMean_normLUT, renderView1)
uMean_normLUTColorBar.Title = 'UMean_norm'
uMean_normLUTColorBar.ComponentTitle = 'Magnitude'

# set color bar visibility
uMean_normLUTColorBar.Visibility = 1

# show color legend
slice_yNormal0p0Display.SetScalarBarVisibility(renderView1, True)

# show color legend
extractBlock_WindsorCompleteDisplay.SetScalarBarVisibility(renderView1, True)

# show color legend
extractBlock_FloorDisplay.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'UMean_norm'
uMean_normPWF = GetOpacityTransferFunction('UMean_norm')
uMean_normPWF.Points = [-1.5, 0.0, 0.5, 0.0, 1.5, 1.0, 0.5, 0.0]
uMean_normPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(extractBlock_WindsorComplete)
# ----------------------------------------------------------------