# HeatMapUtils

''' holds all functionallity which is used for drawing the heatmaps '''


class HeatMapUtils():
    def __init__(self):
        self._grid = 0
        self._grid = [[self._grid for i in range(1000)] for j in range(1000)]

        # now map matrix cells to pixels

        # calculate activity value of each matrix cell
        # based on values display colors on matrix grid
        pass

    # extracts some part of the whole slide image and converts it to a jpg
    def extractToJPG(self, level, centerX, centerY, sampleFactor, topLeft, bottomRight):
        pass

    # calculates matrix grid size for different picture (or layer) sizes
    # returns tuple of (x, y)
    def calculateGrid(self, pixelX, pixelY):
        print(f'pixelxy: {pixelX, pixelY}')

        # just try a 1000 x 1000
        return (1000, 1000)

    def calculateActivityValue(self):
        # add 1 to every matrix cell where eyeData fits the cell
        pass
    