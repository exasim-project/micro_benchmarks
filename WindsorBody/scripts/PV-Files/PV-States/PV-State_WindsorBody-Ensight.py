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
extractBlock_WindsorBase = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorBase.BlockIndices = [10]

# create a new 'Extract Block'
extractBlock_WindsorComplete = ExtractBlock(Input=calculator_CpMean)
extractBlock_WindsorComplete.BlockIndices = [10, 2, 9]

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

# show data from windsorBodycase
windsorBodycaseDisplay = Show(windsorBodycase, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'Co'
coLUT = GetColorTransferFunction('Co')
coLUT.RGBPoints = [137.3688507080078, 0.231373, 0.298039, 0.752941, 282204.184425354, 0.865003, 0.865003, 0.865003, 564271.0, 0.705882, 0.0156863, 0.14902]
coLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'Co'
coPWF = GetOpacityTransferFunction('Co')
coPWF.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]
coPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
windsorBodycaseDisplay.Representation = 'Surface'
windsorBodycaseDisplay.ColorArrayName = ['CELLS', 'Co']
windsorBodycaseDisplay.LookupTable = coLUT
windsorBodycaseDisplay.Ambient = 1.0
windsorBodycaseDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
windsorBodycaseDisplay.SelectOrientationVectors = 'U'
windsorBodycaseDisplay.ScaleFactor = 1.102080011367798
windsorBodycaseDisplay.SelectScaleArray = 'Co'
windsorBodycaseDisplay.GlyphType = 'Arrow'
windsorBodycaseDisplay.GlyphTableIndexArray = 'Co'
windsorBodycaseDisplay.GaussianRadius = 0.05510400056838989
windsorBodycaseDisplay.SetScaleArray = [None, '']
windsorBodycaseDisplay.ScaleTransferFunction = 'PiecewiseFunction'
windsorBodycaseDisplay.OpacityArray = [None, '']
windsorBodycaseDisplay.OpacityTransferFunction = 'PiecewiseFunction'
windsorBodycaseDisplay.DataAxesGrid = 'GridAxesRepresentation'
windsorBodycaseDisplay.PolarAxes = 'PolarAxesRepresentation'
windsorBodycaseDisplay.ScalarOpacityFunction = coPWF
windsorBodycaseDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
windsorBodycaseDisplay.ExtractedBlockIndex = 1

# show data from cellDatatoPointData1
cellDatatoPointData1Display = Show(cellDatatoPointData1, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
cellDatatoPointData1Display.Representation = 'Surface'
cellDatatoPointData1Display.ColorArrayName = ['POINTS', 'Co']
cellDatatoPointData1Display.LookupTable = coLUT
cellDatatoPointData1Display.OSPRayScaleArray = 'Co'
cellDatatoPointData1Display.OSPRayScaleFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.SelectOrientationVectors = 'U'
cellDatatoPointData1Display.ScaleFactor = 1.102080011367798
cellDatatoPointData1Display.SelectScaleArray = 'Co'
cellDatatoPointData1Display.GlyphType = 'Arrow'
cellDatatoPointData1Display.GlyphTableIndexArray = 'Co'
cellDatatoPointData1Display.GaussianRadius = 0.05510400056838989
cellDatatoPointData1Display.SetScaleArray = ['POINTS', 'Co']
cellDatatoPointData1Display.ScaleTransferFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.OpacityArray = ['POINTS', 'Co']
cellDatatoPointData1Display.OpacityTransferFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.DataAxesGrid = 'GridAxesRepresentation'
cellDatatoPointData1Display.PolarAxes = 'PolarAxesRepresentation'
cellDatatoPointData1Display.ScalarOpacityFunction = coPWF
cellDatatoPointData1Display.ScalarOpacityUnitDistance = 0.06024397144867815
cellDatatoPointData1Display.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cellDatatoPointData1Display.ScaleTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cellDatatoPointData1Display.OpacityTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

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

# show data from slice_zNormal0p194
slice_zNormal0p194Display = Show(slice_zNormal0p194, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
slice_zNormal0p194Display.Representation = 'Surface'
slice_zNormal0p194Display.ColorArrayName = ['POINTS', 'Co']
slice_zNormal0p194Display.LookupTable = coLUT
slice_zNormal0p194Display.Ambient = 1.0
slice_zNormal0p194Display.Diffuse = 0.0
slice_zNormal0p194Display.OSPRayScaleArray = 'Co'
slice_zNormal0p194Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_zNormal0p194Display.SelectOrientationVectors = 'U'
slice_zNormal0p194Display.ScaleFactor = 1.102080011367798
slice_zNormal0p194Display.SelectScaleArray = 'Co'
slice_zNormal0p194Display.GlyphType = 'Arrow'
slice_zNormal0p194Display.GlyphTableIndexArray = 'Co'
slice_zNormal0p194Display.GaussianRadius = 0.05510400056838989
slice_zNormal0p194Display.SetScaleArray = ['POINTS', 'Co']
slice_zNormal0p194Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_zNormal0p194Display.OpacityArray = ['POINTS', 'Co']
slice_zNormal0p194Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_zNormal0p194Display.DataAxesGrid = 'GridAxesRepresentation'
slice_zNormal0p194Display.PolarAxes = 'PolarAxesRepresentation'
slice_zNormal0p194Display.ScalarOpacityFunction = coPWF
slice_zNormal0p194Display.ScalarOpacityUnitDistance = 0.2726431319098052
slice_zNormal0p194Display.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_zNormal0p194Display.ScaleTransferFunction.Points = [199.69432067871094, 0.0, 0.5, 0.0, 40974.09765625, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_zNormal0p194Display.OpacityTransferFunction.Points = [199.69432067871094, 0.0, 0.5, 0.0, 40974.09765625, 1.0, 0.5, 0.0]

# show data from slice_xNormal0p63
slice_xNormal0p63Display = Show(slice_xNormal0p63, renderView1, 'UnstructuredGridRepresentation')

# get opacity transfer function/opacity map for 'UMean_norm'
uMean_normPWF = GetOpacityTransferFunction('UMean_norm')
uMean_normPWF.Points = [-1.5, 0.0, 0.5, 0.0, 1.5, 1.0, 0.5, 0.0]
uMean_normPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
slice_xNormal0p63Display.Representation = 'Surface'
slice_xNormal0p63Display.ColorArrayName = ['POINTS', 'UMean_norm']
slice_xNormal0p63Display.LookupTable = uMean_normLUT
slice_xNormal0p63Display.Ambient = 1.0
slice_xNormal0p63Display.Diffuse = 0.0
slice_xNormal0p63Display.OSPRayScaleArray = 'Co'
slice_xNormal0p63Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_xNormal0p63Display.SelectOrientationVectors = 'U'
slice_xNormal0p63Display.ScaleFactor = 0.1919999957084656
slice_xNormal0p63Display.SelectScaleArray = 'Co'
slice_xNormal0p63Display.GlyphType = 'Arrow'
slice_xNormal0p63Display.GlyphTableIndexArray = 'Co'
slice_xNormal0p63Display.GaussianRadius = 0.009599999785423278
slice_xNormal0p63Display.SetScaleArray = ['POINTS', 'Co']
slice_xNormal0p63Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_xNormal0p63Display.OpacityArray = ['POINTS', 'Co']
slice_xNormal0p63Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_xNormal0p63Display.DataAxesGrid = 'GridAxesRepresentation'
slice_xNormal0p63Display.PolarAxes = 'PolarAxesRepresentation'
slice_xNormal0p63Display.ScalarOpacityFunction = uMean_normPWF
slice_xNormal0p63Display.ScalarOpacityUnitDistance = 0.09703699025124317
slice_xNormal0p63Display.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_xNormal0p63Display.ScaleTransferFunction.Points = [189.9053955078125, 0.0, 0.5, 0.0, 14650.4375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_xNormal0p63Display.OpacityTransferFunction.Points = [189.9053955078125, 0.0, 0.5, 0.0, 14650.4375, 1.0, 0.5, 0.0]

# show data from slice_xNormal0p922
slice_xNormal0p922Display = Show(slice_xNormal0p922, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
slice_xNormal0p922Display.Representation = 'Surface'
slice_xNormal0p922Display.ColorArrayName = ['POINTS', 'UMean_norm']
slice_xNormal0p922Display.LookupTable = uMean_normLUT
slice_xNormal0p922Display.Ambient = 1.0
slice_xNormal0p922Display.Diffuse = 0.0
slice_xNormal0p922Display.OSPRayScaleArray = 'Co'
slice_xNormal0p922Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_xNormal0p922Display.SelectOrientationVectors = 'U'
slice_xNormal0p922Display.ScaleFactor = 0.1919999957084656
slice_xNormal0p922Display.SelectScaleArray = 'Co'
slice_xNormal0p922Display.GlyphType = 'Arrow'
slice_xNormal0p922Display.GlyphTableIndexArray = 'Co'
slice_xNormal0p922Display.GaussianRadius = 0.009599999785423278
slice_xNormal0p922Display.SetScaleArray = ['POINTS', 'Co']
slice_xNormal0p922Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_xNormal0p922Display.OpacityArray = ['POINTS', 'Co']
slice_xNormal0p922Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_xNormal0p922Display.DataAxesGrid = 'GridAxesRepresentation'
slice_xNormal0p922Display.PolarAxes = 'PolarAxesRepresentation'
slice_xNormal0p922Display.ScalarOpacityFunction = uMean_normPWF
slice_xNormal0p922Display.ScalarOpacityUnitDistance = 0.09697176154461742
slice_xNormal0p922Display.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_xNormal0p922Display.ScaleTransferFunction.Points = [279.60205078125, 0.0, 0.5, 0.0, 10835.845703125, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_xNormal0p922Display.OpacityTransferFunction.Points = [279.60205078125, 0.0, 0.5, 0.0, 10835.845703125, 1.0, 0.5, 0.0]

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

# show data from extractBlock_WindsorBase
extractBlock_WindsorBaseDisplay = Show(extractBlock_WindsorBase, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
extractBlock_WindsorBaseDisplay.Representation = 'Surface'
extractBlock_WindsorBaseDisplay.ColorArrayName = ['POINTS', 'Co']
extractBlock_WindsorBaseDisplay.LookupTable = coLUT
extractBlock_WindsorBaseDisplay.Ambient = 0.25
extractBlock_WindsorBaseDisplay.OSPRayScaleArray = 'Co'
extractBlock_WindsorBaseDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
extractBlock_WindsorBaseDisplay.SelectOrientationVectors = 'U'
extractBlock_WindsorBaseDisplay.ScaleFactor = 0.0388629749417305
extractBlock_WindsorBaseDisplay.SelectScaleArray = 'Co'
extractBlock_WindsorBaseDisplay.GlyphType = 'Arrow'
extractBlock_WindsorBaseDisplay.GlyphTableIndexArray = 'Co'
extractBlock_WindsorBaseDisplay.GaussianRadius = 0.001943148747086525
extractBlock_WindsorBaseDisplay.SetScaleArray = ['POINTS', 'Co']
extractBlock_WindsorBaseDisplay.ScaleTransferFunction = 'PiecewiseFunction'
extractBlock_WindsorBaseDisplay.OpacityArray = ['POINTS', 'Co']
extractBlock_WindsorBaseDisplay.OpacityTransferFunction = 'PiecewiseFunction'
extractBlock_WindsorBaseDisplay.DataAxesGrid = 'GridAxesRepresentation'
extractBlock_WindsorBaseDisplay.PolarAxes = 'PolarAxesRepresentation'
extractBlock_WindsorBaseDisplay.ScalarOpacityFunction = coPWF
extractBlock_WindsorBaseDisplay.ScalarOpacityUnitDistance = 0.027482106185291198
extractBlock_WindsorBaseDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
extractBlock_WindsorBaseDisplay.ScaleTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 144383.4375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
extractBlock_WindsorBaseDisplay.OpacityTransferFunction.Points = [246.0082550048828, 0.0, 0.5, 0.0, 144383.4375, 1.0, 0.5, 0.0]

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

# show data from calculator_UNorm
calculator_UNormDisplay = Show(calculator_UNorm, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'U_norm'
u_normLUT = GetColorTransferFunction('U_norm')
u_normLUT.RGBPoints = [-0.41649208035420493, 0.231373, 0.298039, 0.752941, 0.5484263741156545, 0.865003, 0.865003, 0.865003, 1.513344828585514, 0.705882, 0.0156863, 0.14902]
u_normLUT.ScalarRangeInitialized = 1.0
u_normLUT.VectorMode = 'Component'

# get opacity transfer function/opacity map for 'U_norm'
u_normPWF = GetOpacityTransferFunction('U_norm')
u_normPWF.Points = [-0.41649208035420493, 0.0, 0.5, 0.0, 1.513344828585514, 1.0, 0.5, 0.0]
u_normPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
calculator_UNormDisplay.Representation = 'Surface'
calculator_UNormDisplay.ColorArrayName = ['POINTS', 'U_norm']
calculator_UNormDisplay.LookupTable = u_normLUT
calculator_UNormDisplay.OSPRayScaleArray = 'Co'
calculator_UNormDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculator_UNormDisplay.SelectOrientationVectors = 'U_norm'
calculator_UNormDisplay.ScaleFactor = 1.102080011367798
calculator_UNormDisplay.SelectScaleArray = 'Co'
calculator_UNormDisplay.GlyphType = 'Arrow'
calculator_UNormDisplay.GlyphTableIndexArray = 'Co'
calculator_UNormDisplay.GaussianRadius = 0.05510400056838989
calculator_UNormDisplay.SetScaleArray = ['POINTS', 'Co']
calculator_UNormDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculator_UNormDisplay.OpacityArray = ['POINTS', 'Co']
calculator_UNormDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculator_UNormDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculator_UNormDisplay.PolarAxes = 'PolarAxesRepresentation'
calculator_UNormDisplay.ScalarOpacityFunction = u_normPWF
calculator_UNormDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
calculator_UNormDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator_UNormDisplay.ScaleTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator_UNormDisplay.OpacityTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# show data from calculator_UMeanNorm
calculator_UMeanNormDisplay = Show(calculator_UMeanNorm, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
calculator_UMeanNormDisplay.Representation = 'Surface'
calculator_UMeanNormDisplay.ColorArrayName = ['POINTS', 'Co']
calculator_UMeanNormDisplay.LookupTable = coLUT
calculator_UMeanNormDisplay.OSPRayScaleArray = 'Co'
calculator_UMeanNormDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculator_UMeanNormDisplay.SelectOrientationVectors = 'U_norm'
calculator_UMeanNormDisplay.ScaleFactor = 1.102080011367798
calculator_UMeanNormDisplay.SelectScaleArray = 'Co'
calculator_UMeanNormDisplay.GlyphType = 'Arrow'
calculator_UMeanNormDisplay.GlyphTableIndexArray = 'Co'
calculator_UMeanNormDisplay.GaussianRadius = 0.05510400056838989
calculator_UMeanNormDisplay.SetScaleArray = ['POINTS', 'Co']
calculator_UMeanNormDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculator_UMeanNormDisplay.OpacityArray = ['POINTS', 'Co']
calculator_UMeanNormDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculator_UMeanNormDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculator_UMeanNormDisplay.PolarAxes = 'PolarAxesRepresentation'
calculator_UMeanNormDisplay.ScalarOpacityFunction = coPWF
calculator_UMeanNormDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
calculator_UMeanNormDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator_UMeanNormDisplay.ScaleTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator_UMeanNormDisplay.OpacityTransferFunction.Points = [137.3688507080078, 0.0, 0.5, 0.0, 564271.0, 1.0, 0.5, 0.0]

# show data from calculator_Cp
calculator_CpDisplay = Show(calculator_Cp, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'Cp'
cpLUT = GetColorTransferFunction('Cp')
cpLUT.AutomaticRescaleRangeMode = 'Never'
cpLUT.RGBPoints = [-1.0, 0.019608, 0.188235, 0.380392, -0.87451, 0.088504, 0.321107, 0.564937, -0.74902, 0.163399, 0.444983, 0.697501, -0.623529, 0.247059, 0.555709, 0.754095, -0.498039, 0.420684, 0.676432, 0.818685, -0.372549, 0.606459, 0.789773, 0.880277, -0.24705900000000003, 0.761476, 0.868512, 0.924567, -0.12156900000000004, 0.878047, 0.925721, 0.951942, 0.00392156999999993, 0.969089, 0.966474, 0.964937, 0.12941200000000008, 0.983852, 0.897578, 0.846828, 0.25490199999999996, 0.982468, 0.800692, 0.706113, 0.38039200000000006, 0.960323, 0.66782, 0.536332, 0.5058820000000002, 0.894579, 0.503806, 0.399769, 0.631373, 0.81707, 0.33218, 0.281046, 0.7568630000000001, 0.728489, 0.155017, 0.197386, 0.8823530000000002, 0.576932, 0.055363, 0.14925, 1.0, 0.403922, 0.0, 0.121569]
cpLUT.ColorSpace = 'Lab'
cpLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'Cp'
cpPWF = GetOpacityTransferFunction('Cp')
cpPWF.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
cpPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
calculator_CpDisplay.Representation = 'Surface'
calculator_CpDisplay.ColorArrayName = ['POINTS', 'Cp']
calculator_CpDisplay.LookupTable = cpLUT
calculator_CpDisplay.OSPRayScaleArray = 'Cp'
calculator_CpDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculator_CpDisplay.SelectOrientationVectors = 'UMean_norm'
calculator_CpDisplay.ScaleFactor = 1.102080011367798
calculator_CpDisplay.SelectScaleArray = 'Cp'
calculator_CpDisplay.GlyphType = 'Arrow'
calculator_CpDisplay.GlyphTableIndexArray = 'Cp'
calculator_CpDisplay.GaussianRadius = 0.05510400056838989
calculator_CpDisplay.SetScaleArray = ['POINTS', 'Cp']
calculator_CpDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculator_CpDisplay.OpacityArray = ['POINTS', 'Cp']
calculator_CpDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculator_CpDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculator_CpDisplay.PolarAxes = 'PolarAxesRepresentation'
calculator_CpDisplay.ScalarOpacityFunction = cpPWF
calculator_CpDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
calculator_CpDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator_CpDisplay.ScaleTransferFunction.Points = [-2.0969502258300783, 0.0, 0.5, 0.0, 1.0400212097167967, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator_CpDisplay.OpacityTransferFunction.Points = [-2.0969502258300783, 0.0, 0.5, 0.0, 1.0400212097167967, 1.0, 0.5, 0.0]

# show data from calculator_CpMean
calculator_CpMeanDisplay = Show(calculator_CpMean, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'CpMean'
cpMeanLUT = GetColorTransferFunction('CpMean')
cpMeanLUT.RGBPoints = [-2.0730439758300783, 0.231373, 0.298039, 0.752941, -0.51686824798584, 0.865003, 0.865003, 0.865003, 1.0393074798583983, 0.705882, 0.0156863, 0.14902]
cpMeanLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'CpMean'
cpMeanPWF = GetOpacityTransferFunction('CpMean')
cpMeanPWF.Points = [-2.0730439758300783, 0.0, 0.5, 0.0, 1.0393074798583983, 1.0, 0.5, 0.0]
cpMeanPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
calculator_CpMeanDisplay.Representation = 'Surface'
calculator_CpMeanDisplay.ColorArrayName = ['POINTS', 'CpMean']
calculator_CpMeanDisplay.LookupTable = cpMeanLUT
calculator_CpMeanDisplay.OSPRayScaleArray = 'CpMean'
calculator_CpMeanDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculator_CpMeanDisplay.SelectOrientationVectors = 'UMean_norm'
calculator_CpMeanDisplay.ScaleFactor = 1.102080011367798
calculator_CpMeanDisplay.SelectScaleArray = 'CpMean'
calculator_CpMeanDisplay.GlyphType = 'Arrow'
calculator_CpMeanDisplay.GlyphTableIndexArray = 'CpMean'
calculator_CpMeanDisplay.GaussianRadius = 0.05510400056838989
calculator_CpMeanDisplay.SetScaleArray = ['POINTS', 'CpMean']
calculator_CpMeanDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculator_CpMeanDisplay.OpacityArray = ['POINTS', 'CpMean']
calculator_CpMeanDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculator_CpMeanDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculator_CpMeanDisplay.PolarAxes = 'PolarAxesRepresentation'
calculator_CpMeanDisplay.ScalarOpacityFunction = cpMeanPWF
calculator_CpMeanDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
calculator_CpMeanDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator_CpMeanDisplay.ScaleTransferFunction.Points = [-2.0730439758300783, 0.0, 0.5, 0.0, 1.0393074798583983, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator_CpMeanDisplay.OpacityTransferFunction.Points = [-2.0730439758300783, 0.0, 0.5, 0.0, 1.0393074798583983, 1.0, 0.5, 0.0]

# show data from calculator_QNorm
calculator_QNormDisplay = Show(calculator_QNorm, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'Q_norm'
q_normLUT = GetColorTransferFunction('Q_norm')
q_normLUT.RGBPoints = [-3036960412887.351, 0.231373, 0.298039, 0.752941, 6058335049719.338, 0.865003, 0.865003, 0.865003, 15153630512326.027, 0.705882, 0.0156863, 0.14902]
q_normLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'Q_norm'
q_normPWF = GetOpacityTransferFunction('Q_norm')
q_normPWF.Points = [-3036960412887.351, 0.0, 0.5, 0.0, 15153630512326.027, 1.0, 0.5, 0.0]
q_normPWF.ScalarRangeInitialized = 1

# trace defaults for the display properties.
calculator_QNormDisplay.Representation = 'Surface'
calculator_QNormDisplay.ColorArrayName = ['POINTS', 'Q_norm']
calculator_QNormDisplay.LookupTable = q_normLUT
calculator_QNormDisplay.OSPRayScaleArray = 'Q_norm'
calculator_QNormDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
calculator_QNormDisplay.SelectOrientationVectors = 'UMean_norm'
calculator_QNormDisplay.ScaleFactor = 1.102080011367798
calculator_QNormDisplay.SelectScaleArray = 'Q_norm'
calculator_QNormDisplay.GlyphType = 'Arrow'
calculator_QNormDisplay.GlyphTableIndexArray = 'Q_norm'
calculator_QNormDisplay.GaussianRadius = 0.05510400056838989
calculator_QNormDisplay.SetScaleArray = ['POINTS', 'Q_norm']
calculator_QNormDisplay.ScaleTransferFunction = 'PiecewiseFunction'
calculator_QNormDisplay.OpacityArray = ['POINTS', 'Q_norm']
calculator_QNormDisplay.OpacityTransferFunction = 'PiecewiseFunction'
calculator_QNormDisplay.DataAxesGrid = 'GridAxesRepresentation'
calculator_QNormDisplay.PolarAxes = 'PolarAxesRepresentation'
calculator_QNormDisplay.ScalarOpacityFunction = q_normPWF
calculator_QNormDisplay.ScalarOpacityUnitDistance = 0.06024397144867815
calculator_QNormDisplay.ExtractedBlockIndex = 1

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator_QNormDisplay.ScaleTransferFunction.Points = [-3036960412887.351, 0.0, 0.5, 0.0, 15153630512326.027, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator_QNormDisplay.OpacityTransferFunction.Points = [-3036960412887.351, 0.0, 0.5, 0.0, 15153630512326.027, 1.0, 0.5, 0.0]

# show data from contour1
contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
contour1Display.Representation = 'Surface'
contour1Display.ColorArrayName = ['POINTS', 'U_norm']
contour1Display.LookupTable = u_normLUT
contour1Display.OSPRayScaleArray = 'Q_norm'
contour1Display.OSPRayScaleFunction = 'PiecewiseFunction'
contour1Display.SelectOrientationVectors = 'UMean_norm'
contour1Display.ScaleFactor = 1.102080011367798
contour1Display.SelectScaleArray = 'Q_norm'
contour1Display.GlyphType = 'Arrow'
contour1Display.GlyphTableIndexArray = 'Q_norm'
contour1Display.GaussianRadius = 0.05510400056838989
contour1Display.SetScaleArray = ['POINTS', 'Q_norm']
contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
contour1Display.OpacityArray = ['POINTS', 'Q_norm']
contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
contour1Display.DataAxesGrid = 'GridAxesRepresentation'
contour1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
contour1Display.ScaleTransferFunction.Points = [100.0, 0.0, 0.5, 0.0, 100.015625, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
contour1Display.OpacityTransferFunction.Points = [100.0, 0.0, 0.5, 0.0, 100.015625, 1.0, 0.5, 0.0]

# show data from slice_Centerline
slice_CenterlineDisplay = Show(slice_Centerline, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice_CenterlineDisplay.Representation = 'Surface'
slice_CenterlineDisplay.ColorArrayName = ['POINTS', 'CpMean']
slice_CenterlineDisplay.LookupTable = cpMeanLUT
slice_CenterlineDisplay.OSPRayScaleArray = 'CpMean'
slice_CenterlineDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_CenterlineDisplay.SelectOrientationVectors = 'UMean_norm'
slice_CenterlineDisplay.ScaleFactor = 0.10430060625076294
slice_CenterlineDisplay.SelectScaleArray = 'CpMean'
slice_CenterlineDisplay.GlyphType = 'Arrow'
slice_CenterlineDisplay.GlyphTableIndexArray = 'CpMean'
slice_CenterlineDisplay.GaussianRadius = 0.005215030312538147
slice_CenterlineDisplay.SetScaleArray = ['POINTS', 'CpMean']
slice_CenterlineDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_CenterlineDisplay.OpacityArray = ['POINTS', 'CpMean']
slice_CenterlineDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_CenterlineDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_CenterlineDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_CenterlineDisplay.ScaleTransferFunction.Points = [-1.4992731798925483, 0.0, 0.5, 0.0, 1.036604236655059, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_CenterlineDisplay.OpacityTransferFunction.Points = [-1.4992731798925483, 0.0, 0.5, 0.0, 1.036604236655059, 1.0, 0.5, 0.0]

# show data from slice_Glasshouse
slice_GlasshouseDisplay = Show(slice_Glasshouse, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice_GlasshouseDisplay.Representation = 'Surface'
slice_GlasshouseDisplay.ColorArrayName = ['POINTS', 'CpMean']
slice_GlasshouseDisplay.LookupTable = cpMeanLUT
slice_GlasshouseDisplay.OSPRayScaleArray = 'CpMean'
slice_GlasshouseDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_GlasshouseDisplay.SelectOrientationVectors = 'UMean_norm'
slice_GlasshouseDisplay.ScaleFactor = 0.08781798481941223
slice_GlasshouseDisplay.SelectScaleArray = 'CpMean'
slice_GlasshouseDisplay.GlyphType = 'Arrow'
slice_GlasshouseDisplay.GlyphTableIndexArray = 'CpMean'
slice_GlasshouseDisplay.GaussianRadius = 0.004390899240970612
slice_GlasshouseDisplay.SetScaleArray = ['POINTS', 'CpMean']
slice_GlasshouseDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_GlasshouseDisplay.OpacityArray = ['POINTS', 'CpMean']
slice_GlasshouseDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_GlasshouseDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_GlasshouseDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_GlasshouseDisplay.ScaleTransferFunction.Points = [-0.6381017338368399, 0.0, 0.5, 0.0, 0.02212577411518879, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_GlasshouseDisplay.OpacityTransferFunction.Points = [-0.6381017338368399, 0.0, 0.5, 0.0, 0.02212577411518879, 1.0, 0.5, 0.0]

# show data from slice_Bumper
slice_BumperDisplay = Show(slice_Bumper, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice_BumperDisplay.Representation = 'Surface'
slice_BumperDisplay.ColorArrayName = ['POINTS', 'CpMean']
slice_BumperDisplay.LookupTable = cpMeanLUT
slice_BumperDisplay.OSPRayScaleArray = 'CpMean'
slice_BumperDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_BumperDisplay.SelectOrientationVectors = 'UMean_norm'
slice_BumperDisplay.ScaleFactor = 0.1057783454656601
slice_BumperDisplay.SelectScaleArray = 'CpMean'
slice_BumperDisplay.GlyphType = 'Arrow'
slice_BumperDisplay.GlyphTableIndexArray = 'CpMean'
slice_BumperDisplay.GaussianRadius = 0.0052889172732830045
slice_BumperDisplay.SetScaleArray = ['POINTS', 'CpMean']
slice_BumperDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_BumperDisplay.OpacityArray = ['POINTS', 'CpMean']
slice_BumperDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_BumperDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_BumperDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_BumperDisplay.ScaleTransferFunction.Points = [-1.5823925946611976, 0.0, 0.5, 0.0, 1.0382434291520375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_BumperDisplay.OpacityTransferFunction.Points = [-1.5823925946611976, 0.0, 0.5, 0.0, 1.0382434291520375, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for coLUT in view renderView1
coLUTColorBar = GetScalarBar(coLUT, renderView1)
coLUTColorBar.Title = 'Co'
coLUTColorBar.ComponentTitle = ''

# set color bar visibility
coLUTColorBar.Visibility = 0

# get color transfer function/color map for 'pMean'
pMeanLUT = GetColorTransferFunction('pMean')
pMeanLUT.RGBPoints = [-1206.6920166015625, 0.231373, 0.298039, 0.752941, -187.75701904296875, 0.865003, 0.865003, 0.865003, 831.177978515625, 0.705882, 0.0156863, 0.14902]
pMeanLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for pMeanLUT in view renderView1
pMeanLUTColorBar = GetScalarBar(pMeanLUT, renderView1)
pMeanLUTColorBar.WindowLocation = 'UpperRightCorner'
pMeanLUTColorBar.Title = 'pMean'
pMeanLUTColorBar.ComponentTitle = ''

# set color bar visibility
pMeanLUTColorBar.Visibility = 0

# get color legend/bar for cpLUT in view renderView1
cpLUTColorBar = GetScalarBar(cpLUT, renderView1)
cpLUTColorBar.WindowLocation = 'UpperLeftCorner'
cpLUTColorBar.Title = 'Cp'
cpLUTColorBar.ComponentTitle = ''

# set color bar visibility
cpLUTColorBar.Visibility = 0

# get color legend/bar for cpMeanLUT in view renderView1
cpMeanLUTColorBar = GetScalarBar(cpMeanLUT, renderView1)
cpMeanLUTColorBar.WindowLocation = 'UpperLeftCorner'
cpMeanLUTColorBar.Title = 'CpMean'
cpMeanLUTColorBar.ComponentTitle = ''

# set color bar visibility
cpMeanLUTColorBar.Visibility = 0

# get color legend/bar for q_normLUT in view renderView1
q_normLUTColorBar = GetScalarBar(q_normLUT, renderView1)
q_normLUTColorBar.WindowLocation = 'UpperLeftCorner'
q_normLUTColorBar.Title = 'Q_norm'
q_normLUTColorBar.ComponentTitle = ''

# set color bar visibility
q_normLUTColorBar.Visibility = 0

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
uLUT.RGBPoints = [-16.659683227539062, 0.231373, 0.298039, 0.752941, 21.937055587768555, 0.865003, 0.865003, 0.865003, 60.53379440307617, 0.705882, 0.0156863, 0.14902]
uLUT.ScalarRangeInitialized = 1.0
uLUT.VectorMode = 'Component'

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.WindowLocation = 'UpperLeftCorner'
uLUTColorBar.Title = 'U'
uLUTColorBar.ComponentTitle = 'X'

# set color bar visibility
uLUTColorBar.Visibility = 0

# get color legend/bar for u_normLUT in view renderView1
u_normLUTColorBar = GetScalarBar(u_normLUT, renderView1)
u_normLUTColorBar.WindowLocation = 'UpperLeftCorner'
u_normLUTColorBar.Title = 'U_norm'
u_normLUTColorBar.ComponentTitle = 'X'

# set color bar visibility
u_normLUTColorBar.Visibility = 0

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

# hide data in view
Hide(windsorBodycase, renderView1)

# hide data in view
Hide(cellDatatoPointData1, renderView1)

# show color legend
slice_yNormal0p0Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_zNormal0p194, renderView1)

# show color legend
slice_xNormal0p63Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_xNormal0p63, renderView1)

# show color legend
slice_xNormal0p922Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_xNormal0p922, renderView1)

# show color legend
extractBlock_WindsorCompleteDisplay.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(extractBlock_WindsorBase, renderView1)

# show color legend
extractBlock_FloorDisplay.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(calculator_UNorm, renderView1)

# hide data in view
Hide(calculator_UMeanNorm, renderView1)

# hide data in view
Hide(calculator_Cp, renderView1)

# hide data in view
Hide(calculator_CpMean, renderView1)

# hide data in view
Hide(calculator_QNorm, renderView1)

# hide data in view
Hide(contour1, renderView1)

# hide data in view
Hide(slice_Centerline, renderView1)

# hide data in view
Hide(slice_Glasshouse, renderView1)

# hide data in view
Hide(slice_Bumper, renderView1)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'pMean'
pMeanPWF = GetOpacityTransferFunction('pMean')
pMeanPWF.Points = [-1206.6920166015625, 0.0, 0.5, 0.0, 831.177978515625, 1.0, 0.5, 0.0]
pMeanPWF.ScalarRangeInitialized = 1

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.Points = [-16.659683227539062, 0.0, 0.5, 0.0, 60.53379440307617, 1.0, 0.5, 0.0]
uPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(extractBlock_WindsorComplete)
# ----------------------------------------------------------------