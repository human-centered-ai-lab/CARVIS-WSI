# ImageSection.py

''' dataframe for ImageSections '''

from copy import copy

class ImageSection():
    def __init__(self,
    file,
    centerX,
    centerY,
    sampleFactor,
    width,
    height,
    roi,
    topLeftX,
    topLeftY,
    topRightX,
    topRightY,
    bottomLeftX,
    bottomLeftY,
    bottomRightX,
    bottomRightY):

        self._fileName = file
        self._centerX = float(centerX)
        self._centerY = float(centerY)
        self._downsampleFactor = float(sampleFactor)
        self._width = float(width)
        self._height = float(height)
        self._viewRoi = roi
        self._topLeftX = float(topLeftX)
        self._topLeftY = float(topLeftY)
        self._topRightX = float(topRightX)
        self._topRightY = float(topRightY)
        self._bottomLeftX = float(bottomLeftX)
        self._bottomLeftY = float(bottomLeftY)
        self._bottomRightX = float(bottomRightX)
        self._bottomRightY = float(bottomRightY)
        self._timestamps = [ ]
        self._eyeTracking = [ ]
    
    # appends timestamps to empty _timestamps list
    # for inheritance reasons
    def addTimestamps(self, timestamps):
        # deep copy
        self._timestamps = timestamps.copy()        

    # appends eye tracking data to empty _eyeTracking list
    # for inheritance reasons
    def addEyeTracking(self, eyeData):
        self._eyeTracking = eyeData.copy()
