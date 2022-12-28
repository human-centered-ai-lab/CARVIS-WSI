# WorkerArgs.py

''' dataframe for Worker Arguments '''

# @param csvFile is path to csvFile
# @param exportLayer layer of wsi to be exported
# @param exportResolution used instead of export layer to directly specify resolution
# @param cellsize set cell size of heatmap
# @param hatchingAlpha set alpha value of hatching pattern
# @param hatchedFlag if set the worker renders the hatching heatmap
# @param viewPathFlag if set the worker renders the viewpath on a base image
# @param viewPathStrength to change default strength of the viewpath line
# @param viewPathColor change the default viewpath line color
# @param viewPathPointSize change the default viewpath point size
# @param viewPathPointColor change the default viewpath point color
# @param cellLabelFlag if set the cell color label is added to bottom of heatmap
# @param roiLabelFlag if set the roi (Image Section) label is added to bottom of heatmap

class WorkerArgs():
    def __init__(self,
      exportLayer,
      exportResolution,
      cellSize,
      hatchingAlpha,
      viewPathStrength,
      viewPathColorStart,
      viewPathColorEnd,
      viewPathPointSize,
      viewPathPointColor,
      heatmapBackgroundAlpha,
      cannyThreashold1,
      cannyThreashold2,
      hatchedFlag=False,
      viewPathFlag=False,
      cellLabelFlag=False,
      roiLabelFlag=False,
      viewPathLabelFlag=False,
      edgeDetectionFlag=False
      ):

        self._exportLayer = exportLayer
        self._exportResolution = exportResolution
        self._cellSize = cellSize
        self._hatchingAlpha = hatchingAlpha
        self._hatchedFlag = hatchedFlag
        self._viewPathFlag = viewPathFlag
        self._viewPathStrength = viewPathStrength
        self._viewPathColorStart = viewPathColorStart,
        self._viewPathColorEnd = viewPathColorEnd,
        self._viewPathPointSize = viewPathPointSize
        self._viewPathPointColor = viewPathPointColor
        self._heatmapBackgroundAlpha = heatmapBackgroundAlpha
        self._cannyThreashold1 = cannyThreashold1
        self._cannyThreashold2 = cannyThreashold2
        self._cellLabelFlag = cellLabelFlag
        self._roiLabelFlag = roiLabelFlag
        self._viewPathLabelFlag = viewPathLabelFlag
        self._edgeDetectionFlag = edgeDetectionFlag
