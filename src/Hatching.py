# Hatching.py

''' dataframe for hatching patterns '''

import sys
from PIL import Image

class Hatching():
    def __init__(self, alpha=170):
        self._hatchingDict = { 's1_m2': Image.open("templates/1_1.png"),
                               's5_m2': Image.open("templates/1_2.png"),
                               'sx_m2': Image.open("templates/1_3.png"),
                               's1_m10': Image.open("templates/2_1.png"),
                               's5_m10': Image.open("templates/2_2.png"),
                               'sx_m10': Image.open("templates/2_3.png"),
                               's1_mx': Image.open("templates/3_1.png"),
                               's5_mx': Image.open("templates/3_2.png"),
                               'sx_mx': Image.open("templates/3_3.png")}
        self._alpha = int(alpha)
    
    # resizes all pattern at once for every wsi
    def resizePattern(self, cellSizeX, cellSizeY):
        for key, image in self._hatchingDict.items():
            self._hatchingDict[key] = image.resize((cellSizeX, cellSizeY))
            
            # putalpha sets plha value of all pixels to same amount.
            # even on transparent ones
            tmpImg = self._hatchingDict[key].copy()
            tmpImg.putalpha(self._alpha)
            self._hatchingDict[key].paste(tmpImg, self._hatchingDict[key])

    # returns hatching image for cell
    def getHatching(self, duration, magnification):
        # dont forget to translate time from ms to s
        duration = duration / 1000
        
        if (duration < 1.0):
            if (magnification < 2.0):
                return self._hatchingDict['s1_m2']
            
            if (magnification >= 2.0 and magnification < 10.0):
                return self._hatchingDict['s1_m10']
            
            if (magnification >= 10.0):
                return self._hatchingDict['s1_mx']
        
        if (duration >= 1.0 and duration < 5.0):
            if (magnification < 2.0):
                return self._hatchingDict['s5_m2']
            
            if (magnification >= 2.0 and magnification < 10.0):
                return self._hatchingDict['s5_m10']
            
            if (magnification >= 10.0):
                return self._hatchingDict['s5_mx']
        
        if (duration >= 5.0):
            if (magnification < 2.0):
                return self._hatchingDict['sx_m2']
            
            if (magnification >= 2.0 and magnification < 10.0):
                return self._hatchingDict['sx_m10']
            
            if (magnification >= 10.0):
                return self._hatchingDict['sx_mx']

    # returns hatching image for cell, based on the given key
    def getHatching(self, key):
        if (not key in self._hatchingDict.keys()):
            sys.stderr.write("ERROR: given key is not valid!")
            return False        
        return self._hatchingDict[key]

    # retuns standard hatching, minimal time, minimal magnification
    def getDefautlHatching(self):
        return self._hatchingDict['s1_m2']