# EyeData.py

''' every EyeData gets an ImageSections assigned '''

class GazePoint():
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

        self._leftX = int(float(gazeLeftX))
        self._leftY = int(float(gazeLeftY))
        self._rightX = int(float(gazeRightX))
        self._rightY = int(float(gazeRightY))
        self._pupilLeft = float(pupilLeft)
        self._pupilRight = float(pupilRight)
        self._distanceLeft = float(distanceLeft)
        self._distanceRight = float(distanceRight)
        self._timeSignal = float(timeSignal)
        self._cameraLeftX = float(cameraLeftX)
        self._cameraLeftY = float(cameraLeftY)
        self._cameraRightX = float(cameraRightX)
        self._cameraRightY = float(cameraRightY)
