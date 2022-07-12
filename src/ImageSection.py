# ImageSection.py
# dataframe for ImageSections

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
        self._timestamps = []
        self._eyeTracking = []