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

        self._gazeLeftX = int(float(gazeLeftX))
        self._gazeLeftY = int(float(gazeLeftY))
        self._gazeRightX = int(float(gazeRightX))
        self._gazeRightY = int(float(gazeRightY))
        self._pupilLeft = float(pupilLeft)
        self._pupilRight = float(pupilRight)
        self._distanceLeft = float(distanceLeft)
        self._distanceRight = float(distanceRight)
        self._timeSignal = float(timeSignal)
        self._cameraLeftX = float(cameraLeftX)
        self._cameraLeftY = float(cameraLeftY)
        self._cameraRightX = float(cameraRightX)
        self._cameraRightY = float(cameraRightY)