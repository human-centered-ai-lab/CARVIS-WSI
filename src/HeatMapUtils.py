# HeatMapUtils

''' holds all functionallity which is used for drawing heatmaps '''

import sys
import math
from PIL import Image, ImageDraw, ImageFont
from Hatching import Hatching

class HeatMapUtils():
    CELL_SIZE_X = 50
    CELL_SIZE_Y = 50
    DISPLAY_X = 1920
    DISPLAY_Y = 1080
    PATH_STRENGTH = 2
    PATH_COLOR = (3, 252, 102)
    POINT_RADIUS = 9
    POINT_COLOR = (3, 252, 161)

    DOWNSAMPLE_1 = (204,255,51, 255)
    DOWNSAMPLE_4 = (102,255,51, 255)
    DOWNSAMPLE_10 = (51,255,102, 255)
    DOWNSAMPLE_20 = (51,255,204, 255)
    DOWNSAMPLE_30 = (51,204,255, 255)
    DOWNSAMPLE_40 = (51,102,255, 255)
    DOWNSAMPLE_X = (102,51,255, 255)

    def __init__(self, pixelCountX, pixelCountY, layer0X, layer0Y, cellSize=50):
        self._grid = 0
        self._exportWidth = int(pixelCountX)
        self._exportHeight = int(pixelCountY)
        self._layer0X = int(layer0X)
        self._layer0Y = int(layer0Y)
        self._gridWidth = math.ceil(self._exportWidth/self.CELL_SIZE_X)
        self._gridHeight = math.ceil(self._exportHeight/self.CELL_SIZE_Y)
        self.CELL_SIZE_X = int(cellSize)
        self.CELL_SIZE_Y = int(cellSize)

        # create 2D grid array for mapping gaze points
        self._grid = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

        # crete 2d grid array for mapping timestamp data
        self._gridTimestamps = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

    # draws view path with data from the eye tracker
    # returns base image with drawn on path
    def drawViewPath(self, baseImage, imageSections, pathStrength=PATH_STRENGTH,
      pathColor=PATH_COLOR, pointRadius=POINT_RADIUS, pointColor=POINT_COLOR):
        image = baseImage.copy()
        imageDraw = ImageDraw.Draw(image)
        lastPoint = None

        pointOffset = int(pointRadius / 2)

        for imageSection in imageSections:
            for gazePoints in imageSection._eyeTracking:

                # drop incomplete points
                if (self.incompleteGazeData(gazePoints)):
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoints)

                # check if mapped point is inside image section frame
                if (self.outsideImageSectionFrame(imageSection, gazePointX, gazePointY)):
                    continue

                # draw point
                imageDraw.ellipse(
                  [
                    (gazePointX - pointOffset,
                    gazePointY - pointOffset),
                    (gazePointX + pointOffset,
                    gazePointY + pointOffset)
                  ], 
                  fill=pointColor, 
                  outline=None, 
                  width=pointRadius)

                # if it is the first 
                if (lastPoint is not None):
                    imageDraw.line([
                      (lastPoint[0], lastPoint[1]), (gazePointX, gazePointY)],
                      fill=pathColor,
                      width=pathStrength,
                      joint=None)

                lastPoint = (gazePointX, gazePointY)

        return image

    # code is from Markus
    # draws a legend on lefty upper corner for the sample rate
    # returns image with drawn on legend
    def drawLegend(self, image):
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

    # draws hatching onto a given .jpg
    # returns image with hatched cell tiles
    def getHatchingHeatmap(self, baseImage, imageSections, alpha):
        image = baseImage.copy()
        
        # see how much time someone has spent looking on one grid cell...
        for imageSection in imageSections:
            # time is in ms
            timeSpent = 0.0
            if (len(imageSection._timestamps) >= 1):
                timeSpent = imageSection._timestamps[-1] - imageSection._timestamps[0]

            # create a grid for every image section...
            imageSectionTimestamps = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]
            
            # additionally grid to save highest sample factor on grid
            gridSampleFactors = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

            for gazePoint in imageSection._eyeTracking:
                # if incomplete data -> drop gazepoint
                if (self.incompleteGazeData(gazePoint)):
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoint)

                # check if gaze point is inside image section frame
                if (self.outsideImageSectionFrame(imageSection, gazePointX, gazePointY)):
                    continue

                # map gazepoints to export resolution
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoint)

                # map to grid
                xCell, yCell = self.mapToCell(gazePointX, gazePointY)

                # edge case protection
                # it is not known why xCell and yCell sometimes exceed the limits
                xCell, yCell = self.cellEdgeCaseProtection(xCell, yCell)

                # grid must be image section dependent
                imageSectionTimestamps[yCell][xCell] += 1

                # now save sampleFactor
                if (imageSection._downsampleFactor > gridSampleFactors[yCell][xCell]):
                    gridSampleFactors[yCell][xCell] = imageSection._downsampleFactor

            # after all eye data inside a imageSection normalize hitmap grid
            normalizedTimeData = self.normalizeGridData(imageSectionTimestamps)

            # now calculate time for each cell and add time to _gridTimestamps
            gridTimeValues = self.mapImageSectionTimesToGrid(normalizedTimeData, timeSpent)

            # add time values to grid
            for y in range(self._gridHeight):
                for x in range(self._gridWidth):
                    self._gridTimestamps[y][x] += gridTimeValues[y][x]

        # draw patterns on grid based on watching time
        # also scale up or down templates based on cell size
        image = self.drawHatching(image, self._gridTimestamps, gridSampleFactors, alpha)
        return image

    # normalizes timestamp data for one image
    # returns grid of normalized values for timestamp between 0 and 1
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

            # catch edge case
            n = 0.0
            if (minValue == maxValue):
                n = 0.5
            else:
                n = (x - minValue) / (maxValue - minValue)
            
            normalizedList.append(n)

        return normalizedList.copy()

    # returns image with drawn on hatching
    def drawHatching(self, image, grid, gridMagnification, alpha):
        hatching = Hatching(alpha)
        hatching.resizePattern(self.CELL_SIZE_X, self.CELL_SIZE_Y)

        for yCell in range(self._gridHeight):
            for xCell in range(self._gridWidth):
                # map the cell to an image pixel coordinate
                cellCenterX = xCell * self.CELL_SIZE_X
                cellCenterY = yCell * self.CELL_SIZE_Y

                if (cellCenterX > self._exportWidth):
                    continue

                if (cellCenterY > self._exportHeight):
                    continue
                
                # drawing part
                hatchingPattern = hatching.getHatching(grid[yCell][xCell], gridMagnification[yCell][xCell])
                image.paste(hatchingPattern, (cellCenterX, cellCenterY), hatchingPattern)

        return image

    # returns grid of time values relative to given imageSection
    # time values represent time spent looking onto cell
    def mapImageSectionTimesToGrid(self, grid, timeSpent):
        timeGrid = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]
        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                timeGrid[y][x] = grid[y][x] * timeSpent
        
        return timeGrid

    # normalizes grid data for heatmap
    # returns new grid in size as old one with values
    # between 0 and 1
    def normalizeGridData(self, grid):
        normalizedGrid = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]
        minValue = sys.maxsize
        maxValue = 0

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                if (grid[y][x] > maxValue):
                    maxValue = grid[y][x]
                if (grid[y][x] < minValue):
                    minValue = grid[y][x]

        for y in range(self._gridHeight):
            for x in range(self._gridWidth):
                value = grid[y][x]

                # catch edge case
                if (value == 0 and minValue == 0 and maxValue == 0):
                    normalizedGrid[y][x] = 0.0
                
                else:
                    normalizedGrid[y][x] = (value - minValue) / (maxValue - minValue)

        return normalizedGrid

    # draws the Image Sections (ROI) on the extracted wsi layer
    # parts of this code is from Markus
    # returns wsi image with rectangle on it
    def drawRoiOnImage(self, baseImage, imageSections, filling=None, lineWidth=10):
        image = baseImage.copy()
        draw = ImageDraw.Draw(image, "RGBA")

        # get normalized timestamp data for all image sections
        normalizedList = self.normalizeTimestampData(imageSections)

        # do this for all image sections
        for index, imageSection in enumerate(imageSections, start=0):
            # scale to export resolution
            scaleFactorX = self._exportWidth / self._layer0X
            scaleFactorY = self._exportHeight / self._layer0Y

            topLeftX = int(imageSection._topLeftX * scaleFactorX)
            topLeftY = int(imageSection._topLeftY * scaleFactorY)
            bottomRightX = int(imageSection._bottomRightX * scaleFactorX)
            bottomRightY = int(imageSection._bottomRightY * scaleFactorY)

            # check sample factor and draw lines in corresponding colors
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
    def extractJPG(self, slide):
        return slide.get_thumbnail((self._exportWidth, self._exportHeight))

    # turns grid values into cell colors and draws them on given image
    # grid values need to be normalized first!
    # returns drawing on image
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
                pixelXEnd = pixelX + self.CELL_SIZE_X
                pixelYEnd = pixelY + self.CELL_SIZE_Y

                if (pixelX > self._exportWidth or pixelXEnd > self._exportWidth):
                    continue

                if (pixelY > self._exportHeight or pixelYEnd > self._exportHeight):
                    continue
                
                # or grid size must be recalculated
                A = gridColors[yCell][xCell][0]
                R = gridColors[yCell][xCell][1]
                G = gridColors[yCell][xCell][2]
                B = gridColors[yCell][xCell][3]

                draw.rectangle((pixelX+1, pixelY+1, pixelXEnd-1, pixelYEnd-1), fill=(R, G, B, A), width=1)

        # draw there a point of calculated color
        return image

    # returns gaze point mapped to the export resolution [x, y]
    def mapGazePoint(self, imageSection, gazePoints):
        # center gaze point
        # relative to monitor upper left corner
        gazeX = int((gazePoints._leftX + gazePoints._rightX) / 2)
        gazeY = int((gazePoints._leftY + gazePoints._rightY) / 2)
        
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
        resolutionFactorX = self._exportWidth / self._layer0X
        resolutionFactorY = self._exportHeight / self._layer0Y

        exportGazeX = int(realGazeX * resolutionFactorX)
        exportGazeY = int(realGazeY * resolutionFactorY)

        # this should be it

        return (exportGazeX, exportGazeY) # how got sometimes negative indexes?

    # returns mapped Cell on grid [x, y]
    def mapToCell(self, gazeX, gazeY):
        xCell = math.ceil(gazeX / self.CELL_SIZE_X)
        yCell = math.ceil(gazeY / self.CELL_SIZE_Y)

        return (xCell, yCell)

    # protects cell mapping from edge cases
    # returns [x, y] cell coordinate
    def cellEdgeCaseProtection(self, xCell, yCell):
        if (yCell >= self._gridHeight):
            yCell = self._gridHeight - 1
        if (yCell < 0):
            yCell = 0
        if (xCell >= self._gridWidth):
            xCell = self._gridWidth - 1
        if (xCell < 0):
            xCell = 0
        
        return xCell, yCell

    # check if gaze point is inside image section frame
    # returns true if point is outside the frame
    def outsideImageSectionFrame(self, imageSection, gazePointX, gazePointY):
        if (gazePointX > imageSection._bottomRightX or gazePointX < 0):
            # when not drop it
            return True
        if (gazePointY > imageSection._bottomLeftY or gazePointY < 0):
            # when not drop it
            return True

        return False

    # checks if given gaze point has complete data
    # returns true if data is incomplete
    def incompleteGazeData(self, gazePoint):
        if (gazePoint._leftX < 0
            or gazePoint._rightX < 0
            or gazePoint._leftY < 0
            or gazePoint._rightY < 0):
            return True
        
        return False

    # calculates heat of grid cells
    # uses GazePoints, which are mapped to export resolution
    # to draw a map on an image
    # returns colored, mostly transparent, cells rendered onto a .jpg
    def getHeatmap(self, baseImage, imageSections):
        image = baseImage.copy()
        for imageSection in imageSections:
            for gazePoints in imageSection._eyeTracking:

                # if incomplete data -> drop gazepoint
                if (self.incompleteGazeData(gazePoints)):
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoints)

                # check if mapped point is inside image section frame
                if (self.outsideImageSectionFrame(imageSection, gazePointX, gazePointY)):
                    continue                

                # map gaze point to cell in grid and increase hit counter
                xCell, yCell = self.mapToCell(gazePointX, gazePointY)

                # edge case protection
                # it is not known why xCell and yCell sometimes exceed the limits
                xCell, yCell = self.cellEdgeCaseProtection(xCell, yCell)
                
                self._grid[yCell][xCell] += 1
        
        # normalize grid data
        normalizedGridData = self.normalizeGridData(self._grid)
        
        # draw grid values on image and return
        return self.drawGridValues(image, normalizedGridData)
