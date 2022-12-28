# HatchingGridCell.py

''' holds cell data for hatching. every grid cell in Hatching Heatmap gets one instance assigned '''

class HatchingGridCell:    
    def __init__(self):
        self._hatchingGridCellFlags = { 's1_m2': False,
                                        's5_m2': False,
                                        'sx_m2': False,
                                        's1_m10': False,
                                        's5_m10': False,
                                        'sx_m10': False,
                                        's1_mx': False,
                                        's5_mx': False,
                                        'sx_mx': False }

    # returns flag of given key
    def getHatchingFlag(self, key):
        return self._hatchingGridCellFlags[key]

    # returns a list of all hatching flags
    def getAllHatchingFlags(self):
        flagList = [ ]
        for key in self._hatchingGridCellFlags:
            if (self._hatchingGridCellFlags[key]):
                flagList.append([key])
        return flagList.copy()

    # sets the flag in _hatchingGridCellFlags for use in drawHatchingGrid
    def setHatchingFlag(self, duration, magnification):
        if (duration < 1.0):
            if (magnification < 2.0):
                self._hatchingGridCellFlags['s1_m2'] = True
            
            if (magnification >= 2.0 and magnification < 10.0):
                self._hatchingGridCellFlags['s5_m2'] = True
            
            if (magnification >= 10.0):
                self._hatchingGridCellFlags['sx_m2'] = True
        
        if (duration >= 1.0 and duration < 5.0):
            if (magnification < 2.0):
                self._hatchingGridCellFlags['s1_m10'] = True
            
            if (magnification >= 2.0 and magnification < 10.0):
                self._hatchingGridCellFlags['s5_m10'] = True

            if (magnification >= 10.0):
                self._hatchingGridCellFlags['sx_m10'] = True
        
        if (duration >= 5.0):
            if (magnification < 2.0):
                self._hatchingGridCellFlags['s1_mx'] = True
            
            if (magnification >= 2.0 and magnification < 10.0):
                self._hatchingGridCellFlags['s5_mx'] = True
            
            if (magnification >= 10.0):
                self._hatchingGridCellFlags['sx_mx'] = True

    # returns list of keys
    def getKeys(self):
        return self._hatchingGridCellFlags.keys()

    # returns list of true valued keys
    def getActiveKeys(self):
        activeFlagList = [ ]
        for key in self._hatchingGridCellFlags:
            if (self._hatchingGridCellFlags[key]):
                activeFlagList.append(key)
        return activeFlagList

    # gets number of true set flags
    def getNumOfSetFlags(self):
        flagCounter = 0
        for key in self._hatchingGridCellFlags:
            if (self._hatchingGridCellFlags[key]):
                flagCounter += 1
        return flagCounter