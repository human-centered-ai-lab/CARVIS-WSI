# HeatMapUtils

''' holds all functionallity which is used for drawing the heatmaps '''

# a fine grid needs to be layed over the image. when an eyeData point
# hits a grid cell, it's counter will be increased. then the grid will get
# colorised according to it cell's hit rate and displayed over the original
# wsi image layer.
#
# all eyeData points need to be calculated back to the original image pixels at level 0.
# data for this is in each corresponding ImageSection.

import sys
import math
from PIL import Image, ImageDraw, ImageFont

class HeatMapUtils():
    CELL_SIZE_X = 100
    CELL_SIZE_Y = 100
    DISPLAY_X = 1920
    DISPLAY_Y = 1080

    DOWNSAMPLE_1 = (204,255,51, 255)
    DOWNSAMPLE_4 = (102,255,51, 255)
    DOWNSAMPLE_10 = (51,255,102, 255)
    DOWNSAMPLE_20 = (51,255,204, 255)
    DOWNSAMPLE_30 = (51,204,255, 255)
    DOWNSAMPLE_40 = (51,102,255, 255)
    DOWNSAMPLE_X = (102,51,255, 255)

    def __init__(self, pixelCountX, pixelCountY, layer0X, layer0Y):
        self._grid = 0
        self.extractedSizeX = int(pixelCountX)
        self.extractedSizeY = int(pixelCountY)
        self._layer0X = int(layer0X)
        self._layer0Y = int(layer0Y)
        print(f'extracted size[x,y]: {self.extractedSizeX, self.extractedSizeY}')
        print(f'image width/height ratio: {self.extractedSizeX/self.extractedSizeY}')

        self._gridWidth = math.ceil(self.extractedSizeX/self.CELL_SIZE_X)
        self._gridHeight = math.ceil(self.extractedSizeY/self.CELL_SIZE_Y)
        print(f'grid width/height ratio: {self._gridWidth/self._gridHeight}')

        # create 2D grid [array] for mapping heat
        # [height, width] (for all rows make the columns)
        self._grid = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

    # code is from Markus
    # draws a legend on lefty upper corner for the sample rate
    # returns image with drawn on legend
    def drawLegend(self, image):
        # https://stackoverflow.com/questions/41405632/draw-a-rectangle-and-a-text-in-it-using-pil
        draw = ImageDraw.Draw(image, "RGBA")

        # draw samplerates and colors
        font = ImageFont.truetype("arial.ttf", 100)
        #font = None
        draw.rectangle((0, 0, 800, 100), fill=self.DOWNSAMPLE_1, width=25)
        draw.text((0, 0),"Downsample < 1",(0,0,0), font = font)
        draw.rectangle((0, 100, 800, 200), fill=self.DOWNSAMPLE_4, width=25)
        draw.text((0, 100),"Downsample < 4",(0,0,0), font = font)
        draw.rectangle((0, 200, 800, 300), fill=self.DOWNSAMPLE_10, width=25)
        draw.text((0, 200),"Downsample < 10",(0,0,0), font = font)
        draw.rectangle((0, 300, 800, 400), fill=self.DOWNSAMPLE_20, width=25)
        draw.text((0, 300),"Downsample < 20",(0,0,0), font = font)
        draw.rectangle((0, 400, 800, 500), fill=self.DOWNSAMPLE_30, width=25)
        draw.text((0, 400),"Downsample < 30",(0,0,0), font = font)
        draw.rectangle((0, 500, 800, 600), fill=self.DOWNSAMPLE_40, width=25)
        draw.text((0, 500),"Downsample < 40",(0,0,0), font = font)
        draw.rectangle((0, 600, 800, 700), fill=self.DOWNSAMPLE_X, width=25)
        draw.text((0, 600),"Downsample > 40",(0,0,0), font = font)
        
        return image

    # draws the path of eyes on the wsi extracted layer
    # returns wsi layer with path drawing on it
    def drawViewPath(self, image, viewPoints, color, lineThicknes):
        # ToDo if needed
        pass

    # normalizes timestamp data for one image
    # returns list of normalized values for timestamp
    def normalizeTimestampData(self, imageSections):
        normalizedList = [ ]
        minValue = sys.maxsize
        maxValue = 0

        for imageSection in imageSections:
            timestampNum = len(imageSection._timestamps)
            if (timestampNum > maxValue):
                maxValue = timestampNum
            if (timestampNum < minValue):
                minValue = timestampNum
        
        for imageSection in imageSections:
            x = len(imageSection._timestamps)
            n = (x - minValue) / (maxValue - minValue)
            normalizedList.append(n)

        return normalizedList.copy()

    # normalizes grid data for heatmap
    # returns new grid in size as old one with values
    # between 0 and 1
    def normalizeGridData(self):
        normalizedGrid = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]
        minValue = sys.maxsize
        maxValue = 0

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                if (self._grid[y][x] > maxValue):
                    maxValue = self._grid[y][x]
                if (self._grid[y][x] < minValue):
                    minValue = self._grid[y][x]

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                value = self._grid[y][x]
                normalizedGrid[y][x] = (value - minValue) / (maxValue - minValue)

        return normalizedGrid # deep copy 2d array?

    # draws the Image Sections (ROI) on the extracted wsi layer
    # parts of this code is from Markus
    # returns wsi image with rectangle on it
    def drawRoiOnImage(self, image, imageSections, filling=None, lineWidth=10):
        draw = ImageDraw.Draw(image, "RGBA") # (200, 100, 0, 5) | '#9EFF00'

        # get normalized timestamp data for all image sections
        normalizedList = self.normalizeTimestampData(imageSections)

        # do this for all image sections
        for index, imageSection in enumerate(imageSections, start=0):

            topLeftX = imageSection._topLeftX / imageSection._downsampleFactor
            topLeftY = imageSection._topLeftY / imageSection._downsampleFactor
            bottomRightX = imageSection._bottomRightX / imageSection._downsampleFactor
            bottomRightY = imageSection._bottomRightY / imageSection._downsampleFactor

            sampleFactor = imageSection._downsampleFactor
            outlineColor = (0, 0, 0)

            if (sampleFactor < 1):
                outlineColor = self.DOWNSAMPLE_1
            
            elif (sampleFactor < 4 and sampleFactor >= 1):
                outlineColor = self.DOWNSAMPLE_4
            
            elif (sampleFactor < 10 and sampleFactor >= 4):
                outlineColor = self.DOWNSAMPLE_10
            
            elif (sampleFactor < 20 and sampleFactor >= 10):
                outlineColor = self.DOWNSAMPLE_20

            elif (sampleFactor < 30 and sampleFactor >= 20):
                outlineColor = self.DOWNSAMPLE_30
            
            elif (sampleFactor < 40 and sampleFactor >= 30):
                outlineColor = self.DOWNSAMPLE_30
            
            elif (sampleFactor > 40):
                outlineColor = self.DOWNSAMPLE_X

            outlineing=(
              outlineColor[0],
              outlineColor[1],
              outlineColor[2],
              int(100 * normalizedList[index]))

            draw.rectangle((
                topLeftX,
                topLeftY,
                bottomRightX,
                bottomRightY),
                fill=filling,
                outline=outlineing,
                width=lineWidth)

        return image

    # extracts a "level" (only resolution) of the whole slide image and converts it to a jpg
    # returns the level on success or None on failure
    '''
    Note: when there are some issues with extracting an level/roi, 
          this might help: https://www.linuxfromscratch.org/blfs/view/cvs/general/pixman.html
    '''
    def extractJPG(self, slide):
        return slide.get_thumbnail((self.extractedSizeX, self.extractedSizeY))

    # draws the grid values onto given image
    # grid values need to be normalized first!
    # returns drawn on image
    def drawGridValues(self, image, gridValues):
        draw = ImageDraw.Draw(image, "RGBA")
        # [width, height] (for all rows make the columns)
        gridColors = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

        # first get through array of values to make array of colors
        for yCell in range(self._gridHeight):
            for xCell in range(self._gridWidth):
                A = (int(255 * gridValues[yCell][xCell]))
                B = 205
                G = 244
                R = 50
                gridColors[yCell][xCell] = (A, R, G, B)

        # go through all grid cells and get the center position (of the cell) on the image
        for yCell in range(self._gridHeight):
            for xCell in range(self._gridWidth):
                # map the cell to an image pixel coordinate
                pixelX = xCell * self.CELL_SIZE_X
                pixelY = yCell * self.CELL_SIZE_Y
                pixelXEnd = pixelX + 100
                pixelYEnd = pixelY + 100

                if (pixelX > self.extractedSizeX or pixelXEnd > self.extractedSizeX):
                    continue

                if (pixelY > self.extractedSizeY or pixelYEnd > self.extractedSizeY):
                    continue
                
                # or grid size must be recalculated
                A = gridColors[yCell][xCell][0]
                R = gridColors[yCell][xCell][1]
                G = gridColors[yCell][xCell][2]
                B = gridColors[yCell][xCell][3]

                draw.rectangle((pixelX+10, pixelY+10, pixelXEnd-10, pixelYEnd-10), fill=(R, G, B, A), width=1)

        # draw there a point of calculated color
        return image

    # returns gaze point mapped to export resolution
    def mapGazePoint(self, imageSection, eyeData):
        # center gaze point
        # relative to monitor upper left corner
        gazeX = int((eyeData._gazeLeftX + eyeData._gazeRightX) / 2)
        gazeY = int((eyeData._gazeLeftY + eyeData._gazeRightY) / 2)
        
        # eye data (or "gaze point") is relative to upper left corner of monitor
        # need to turn monitor related position into wsi (layer 0) related position

        # calculate dead part on recording monitor, which is the iMotions window
        deadWidth = self.DISPLAY_X - imageSection._width
        deadHeight = self.DISPLAY_Y - imageSection._height

        # current height, current width are relative to wsi
        # calculate gaze point relative to frame. image section is shown on monitor
        # with iMotions window
        relativeGazePointX = gazeX - deadWidth
        relativeGazePointY = gazeY - deadHeight

        # next step is to calculate gaze point relative to wsi
        # image section corner points (view roi) are relative to wsi so use them
        realGazeX = imageSection._topLeftX + relativeGazePointX
        realGazeY = imageSection._topLeftY + relativeGazePointY

        # now map gaze points to export resolution
        resolutionFactorX = self.extractedSizeX / self._layer0X
        resolutionFactorY = self.extractedSizeY / self._layer0Y

        exportGazeX = int(realGazeX * resolutionFactorX)
        exportGazeY = int(realGazeY * resolutionFactorY)

        # this should be it

        return (exportGazeX, exportGazeY) # how got sometimes negative indexes?

    # returns mapped Cell on grid [x, y]
    def mapToCell(self, gazeX, gazeY):
        xCell = math.ceil(gazeX / self.CELL_SIZE_X)
        yCell = math.ceil(gazeY / self.CELL_SIZE_Y)

        return (xCell, yCell)

    # calculates heat of grid cells which stretch over an image
    # maps eyeData coordinates onto the grid cells. each hit increases the heat of the cell
    # returns colored (but transparent) cells rendered onto a .jpg
    def getHeatmap(self, image, imageSections):
        for imageSection in imageSections:
            for eyeData in imageSection._eyeTracking:

                # if incomplete data -> drop datapoint
                if (eyeData._gazeLeftX < 0
                  or eyeData._gazeRightX < 0
                  or eyeData._gazeLeftY < 0
                  or eyeData._gazeRightY < 0):
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, eyeData)
                print(f'mapped gaze point (L0): {gazePointX} {gazePointY}')

                # check if gaze point is inside image section frame
                if (gazePointX > imageSection._bottomRightX or gazePointX < 0):
                    # when not drop it
                    continue
                if (gazePointY > imageSection._bottomLeftY or gazePointY < 0):
                    # when not drop it
                    continue

                # map gaze point to cell in grid and increase hit counter
                xCell, yCell = self.mapToCell(gazePointX, gazePointY)
                self._grid[yCell][xCell] += 1
        
        # normalize grid data
        normalizedGridData = self.normalizeGridData()
        
        # draw grid values on image and return
        return self.drawGridValues(image, normalizedGridData)
