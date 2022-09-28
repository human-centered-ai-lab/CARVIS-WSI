# Hatching.py

''' dataframe for hatching patterns '''

from PIL import Image, ImageDraw, ImageFont

class Hatching():
    def __init__(self):
        self._hatchingDict = { 's1_m2': Image.open("templates/1_1.png"),
                               's5_m2': Image.open("templates/1_2.png"),
                               'sx_m2': Image.open("templates/1_3.png"),
                               's1_m10': Image.open("templates/2_1.png"),
                               's5_m10': Image.open("templates/2_2.png"),
                               'sx_m10': Image.open("templates/2_3.png"),
                               's1_mx': Image.open("templates/3_1.png"),
                               's5_mx': Image.open("templates/3_2.png"),
                               'sx_mx': Image.open("templates/3_3.png")}
    
    # resizes all pattern at once for every wsi
    def resizePattern(self, cellSizeX, cellSizeY):
        print(f'cell size: {cellSizeX, cellSizeY}')
        for key, image in self._hatchingDict.items():
            self._hatchingDict[key] = image.resize((cellSizeX, cellSizeY))
            #self._hatchingDict[key].putalpha(255)


    # returns hatching image for cell
    def getHatching(self, duration, magnification):
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
