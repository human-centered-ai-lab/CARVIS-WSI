# EyeData.py

''' every EyeData gets an ImageSections assigned '''

class EyeData():
    def __init__(self,
      gazeLeftX,
      gazeLeftY,
      gazeRightX,
      gazeRightY,
      pupilLeft,
      pupilRight,
      timeSignal,
      distanceLeft,
      distanceRight,
      cameraLeftX,
      cameraLeftY,
      cameraRightX,
      cameraRightY):

        self._gazeLeftX = gazeLeftX
        self._gazeLeftY = gazeLeftY
        self._gazeRightX = gazeRightX
        self._gazeRightY = gazeRightY
        self._pupilLeft = pupilLeft
        self._pupilRight = pupilRight
        self.distanceLeft = distanceLeft
        self._distanceRight = distanceRight
        self._timeSignal = timeSignal
        self._cameraLeftX = cameraLeftX
        self._cameraLeftY = cameraLeftY
        self._cameraRightX = cameraRightX
        self._cameraRightY = cameraRightY