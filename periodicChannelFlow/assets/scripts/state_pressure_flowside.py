# state file generated using paraview version 5.11.1
import paraview
paraview.compatibility.major = 5
paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# get the material library
materialLibrary1 = GetMaterialLibrary()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [1885, 889]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.OrientationAxesLabelColor = [0.0, 0.0, 0.0]
renderView1.OrientationAxesOutlineColor = [0.0, 0.0, 0.0]
renderView1.CenterOfRotation = [0.375, 1.0, 0.20000000298023224]
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraPosition = [0.27850612798887736, 0.9976774602417378, 3.5652197118031803]
renderView1.CameraFocalPoint = [0.2785061279888747, 0.9976774602417378, -0.37500000000000017]
renderView1.CameraViewUp = [1.0, 0.0, -6.762402743985545e-16]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 0.47574604725755587
renderView1.CameraParallelProjection = 1
renderView1.UseColorPaletteForBackground = 0
renderView1.Background = [1.0, 1.0, 1.0]
renderView1.BackEnd = 'OSPRay raycaster'
renderView1.OSPRayMaterialLibrary = materialLibrary1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(1885, 889)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'OpenFOAMReader'
casefoam = OpenFOAMReader(registrationName='case.foam', FileName='case.foam')
casefoam.CaseType = 'Decomposed Case'
casefoam.MeshRegions = ['internalMesh']
casefoam.CellArrays = ['U', 'UMean', 'UPrime2Mean', 'p', 'pMean', 'pPrime2Mean', 'processorID']
casefoam.Decomposepolyhedra = 0
casefoam.Readzones = 1

# create a new 'Extract Block'
extractBlock1 = ExtractBlock(registrationName='ExtractBlock1', Input=casefoam)
extractBlock1.Selectors = ['/Root/zones']

# create a new 'Slice'
slice1 = Slice(registrationName='Slice1', Input=extractBlock1)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.Triangulatetheslice = 0
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [0.375, 1.0, 0.20000000298023224]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice1.HyperTreeGridSlicer.Origin = [0.375, 1.0, 0.20000000298023224]

# create a new 'Slice'
slice2 = Slice(registrationName='Slice2', Input=casefoam)
slice2.SliceType = 'Plane'
slice2.HyperTreeGridSlicer = 'Plane'
slice2.Triangulatetheslice = 0
slice2.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice2.SliceType.Origin = [0.375, 1.0, 0.20000000298023224]
slice2.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice2.HyperTreeGridSlicer.Origin = [0.375, 1.0, 0.20000000298023224]

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from slice1
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice1Display.Representation = 'Surface'
slice1Display.AmbientColor = [0.0, 0.0, 0.0]
slice1Display.ColorArrayName = ['POINTS', '']
slice1Display.DiffuseColor = [0.0, 0.0, 0.0]
slice1Display.LineWidth = 2.0
slice1Display.RenderLinesAsTubes = 1
slice1Display.SelectTCoordArray = 'None'
slice1Display.SelectNormalArray = 'None'
slice1Display.SelectTangentArray = 'None'
slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice1Display.SelectOrientationVectors = 'U'
slice1Display.ScaleFactor = 0.2
slice1Display.SelectScaleArray = 'p'
slice1Display.GlyphType = 'Arrow'
slice1Display.GlyphTableIndexArray = 'p'
slice1Display.GaussianRadius = 0.01
slice1Display.SetScaleArray = [None, '']
slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice1Display.OpacityArray = [None, '']
slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice1Display.DataAxesGrid = 'GridAxesRepresentation'
slice1Display.PolarAxes = 'PolarAxesRepresentation'
slice1Display.SelectInputVectors = [None, '']
slice1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice1Display.OSPRayScaleFunction.Points = [-61.0421023556655, 0.0, 0.5, 0.0, 25.57078845875926, 1.0, 0.5, 0.0]

# show data from slice2
slice2Display = Show(slice2, renderView1, 'GeometryRepresentation')

# get 2D transfer function for 'p'
pTF2D = GetTransferFunction2D('p')
pTF2D.ScalarRangeInitialized = 1
pTF2D.Range = [-0.02, 0.02, 0.0, 1.0]

# get color transfer function/color map for 'p'
pLUT = GetColorTransferFunction('p')
pLUT.AutomaticRescaleRangeMode = 'Never'
pLUT.TransferFunction2D = pTF2D
pLUT.RGBPoints = [-0.02, 0.831373, 0.909804, 0.980392, -0.0195, 0.74902, 0.862745, 0.960784, -0.019, 0.694118, 0.827451, 0.941176, -0.018000000000000002, 0.568627, 0.760784, 0.921569, -0.017, 0.45098, 0.705882, 0.901961, -0.016, 0.345098, 0.643137, 0.858824, -0.015, 0.247059, 0.572549, 0.819608, -0.014, 0.180392, 0.521569, 0.780392, -0.013600000000000001, 0.14902, 0.490196, 0.74902, -0.0128, 0.129412, 0.447059, 0.709804, -0.012, 0.101961, 0.427451, 0.690196, -0.011600000000000001, 0.094118, 0.403922, 0.658824, -0.0112, 0.090196, 0.392157, 0.639216, -0.0108, 0.082353, 0.368627, 0.619608, -0.010400000000000001, 0.070588, 0.352941, 0.6, -0.01, 0.066667, 0.329412, 0.568627, -0.0096, 0.07451, 0.313725, 0.541176, -0.0092, 0.086275, 0.305882, 0.509804, -0.008799999999999999, 0.094118, 0.286275, 0.478431, -0.008400000000000001, 0.101961, 0.278431, 0.45098, -0.008, 0.109804, 0.266667, 0.411765, -0.007600000000000001, 0.113725, 0.258824, 0.380392, -0.0072, 0.113725, 0.25098, 0.34902, -0.006799999999999999, 0.109804, 0.266667, 0.321569, -0.0063999999999999994, 0.105882, 0.301961, 0.262745, -0.006000000000000002, 0.094118, 0.309804, 0.243137, -0.005600000000000001, 0.082353, 0.321569, 0.227451, -0.0052, 0.07451, 0.341176, 0.219608, -0.0048000000000000004, 0.070588, 0.360784, 0.211765, -0.004399999999999999, 0.066667, 0.380392, 0.215686, -0.004, 0.062745, 0.4, 0.176471, -0.002999999999999999, 0.07451, 0.419608, 0.145098, -0.0019999999999999983, 0.086275, 0.439216, 0.117647, -0.0010000000000000009, 0.121569, 0.470588, 0.117647, 0.0, 0.184314, 0.501961, 0.14902, 0.0010000000000000009, 0.254902, 0.541176, 0.188235, 0.0020000000000000018, 0.32549, 0.580392, 0.231373, 0.002999999999999999, 0.403922, 0.619608, 0.278431, 0.004, 0.501961, 0.670588, 0.333333, 0.0052, 0.592157, 0.729412, 0.4, 0.006000000000000002, 0.741176, 0.788235, 0.490196, 0.0068000000000000005, 0.858824, 0.858824, 0.603922, 0.007999999999999997, 0.921569, 0.835294, 0.580392, 0.009999999999999998, 0.901961, 0.729412, 0.494118, 0.012, 0.858824, 0.584314, 0.388235, 0.014000000000000002, 0.8, 0.439216, 0.321569, 0.016000000000000004, 0.678431, 0.298039, 0.203922, 0.018, 0.54902, 0.168627, 0.109804, 0.019, 0.478431, 0.082353, 0.047059, 0.02, 0.45098, 0.007843, 0.0]
pLUT.ColorSpace = 'RGB'
pLUT.NanColor = [0.25, 0.0, 0.0]
pLUT.NumberOfTableValues = 40
pLUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
slice2Display.Representation = 'Surface'
slice2Display.ColorArrayName = ['CELLS', 'p']
slice2Display.LookupTable = pLUT
slice2Display.LineWidth = 2.0
slice2Display.SelectTCoordArray = 'None'
slice2Display.SelectNormalArray = 'None'
slice2Display.SelectTangentArray = 'None'
slice2Display.OSPRayScaleArray = 'U'
slice2Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice2Display.SelectOrientationVectors = 'U'
slice2Display.ScaleFactor = 0.2
slice2Display.SelectScaleArray = 'p'
slice2Display.GlyphType = 'Arrow'
slice2Display.GlyphTableIndexArray = 'p'
slice2Display.GaussianRadius = 0.01
slice2Display.SetScaleArray = ['POINTS', 'U']
slice2Display.ScaleTransferFunction = 'PiecewiseFunction'
slice2Display.OpacityArray = ['POINTS', 'U']
slice2Display.OpacityTransferFunction = 'PiecewiseFunction'
slice2Display.DataAxesGrid = 'GridAxesRepresentation'
slice2Display.PolarAxes = 'PolarAxesRepresentation'
slice2Display.SelectInputVectors = ['POINTS', 'U']
slice2Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice2Display.OSPRayScaleFunction.Points = [-61.0421023556655, 0.0, 0.5, 0.0, 25.57078845875926, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice2Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.3751018047332764, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice2Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.3751018047332764, 1.0, 0.5, 0.0]
slice2Display.RenderLinesAsTubes = 0
# setup the color legend parameters for each legend in this view

# get color legend/bar for pLUT in view renderView1
pLUTColorBar = GetScalarBar(pLUT, renderView1)
pLUTColorBar.AutoOrient = 0
pLUTColorBar.Orientation = 'Horizontal'
pLUTColorBar.WindowLocation = 'Any Location'
pLUTColorBar.Position = [0.6364190981432362, 0.03462317210348709]
pLUTColorBar.Title = 'p'
pLUTColorBar.ComponentTitle = ''
pLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
pLUTColorBar.TitleFontFamily = 'File'
pLUTColorBar.TitleFontFile = '/home/hetmann/Downloads/BarlowSemiCondensed-Bold.ttf'
pLUTColorBar.TitleBold = 1
pLUTColorBar.TitleFontSize = 35
pLUTColorBar.LabelColor = [0.0, 0.0, 0.0]
pLUTColorBar.LabelFontFamily = 'File'
pLUTColorBar.LabelFontFile = '/home/hetmann/Downloads/BarlowSemiCondensed-Light.ttf'
pLUTColorBar.LabelBold = 1
pLUTColorBar.LabelFontSize = 32
pLUTColorBar.ScalarBarThickness = 45
pLUTColorBar.ScalarBarLength = 0.3299999999999994
pLUTColorBar.CustomLabels = [700.0, 701.0, 702.0, 703.0, 704.0, 705.0, 706.0, 707.0, 708.0, 709.0, 710.0]
pLUTColorBar.AddRangeLabels = 0

# set color bar visibility
pLUTColorBar.Visibility = 1

# show color legend
slice2Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'p'
pPWF = GetOpacityTransferFunction('p')
pPWF.Points = [-0.02, 0.0, 0.5, 0.0, 0.02, 1.0, 0.5, 0.0]
pPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# restore active source
SetActiveSource(slice2)
# ----------------------------------------------------------------


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')

SaveScreenshot("../plots/fig_deco_side_pressure.png", renderView1, ImageResolution=(1885, 889))