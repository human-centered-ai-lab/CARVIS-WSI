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
    topLeft,
    topRight,
    bottomLeft,
    bottomRight):

        self._fileName = file
        self._centerX = centerX
        self._centerY = centerY
        self._downsampleFactor = sampleFactor
        self._width = width
        self._height = height
        self._viewRoi = roi
        self._topLeft = topLeft
        self._topRigth = topRight
        self._bottomLeft = bottomLeft
        self._bottomRight = bottomRight
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