# HeatMapUtils

''' holds all functionallity which is used for drawing heatmaps '''

import sys
import math
import cv2 as cv
import numpy as np
from os.path import exists
from textwrap import fill
from PIL import Image, ImageDraw, ImageFont
from Hatching import Hatching
from HatchingGridCell import HatchingGridCell as HGC

class HeatMapUtils():
    CAN_MAG = 40
    CELL_SIZE_X = 50
    CELL_SIZE_Y = 50
    MIN_ROI_LEGEND_SIZE = 50
    MAX_ROI_LEGEND_SIZE = 75
    DISPLAY_X = 1920
    DISPLAY_Y = 1080
    PATH_STRENGTH = 2
    POINT_RADIUS = 9
    POINT_COLOR = (3, 252, 161, 255)
    PATH_START_COLOR = (127, 191, 15, 255)
    PATH_END_COLOR = (15, 109, 191, 255)

    MIN_ROI_ALPHA = 0.07

    FONT_FILE = "templates/arial.ttf"

    MAG_40_SCAN_RES = 100000
    MAG_20_SCAN_RES = 50000
    MAG_10_SCAN_RES = 25000
    MAG_5_SCAN_RES = 12500

    CANNY_PARAM1 = 100
    CANNY_PARAM2 = 400

    MAGNIFICATION_MIN = (255, 94, 0, 255)
    MAGNIFICATION_2_5 = (183, 255, 0, 255)
    MAGNIFICATION_5 = (0, 255, 0, 255)
    MAGNIFICATION_10 = (51, 255, 204, 255)
    MAGNIFICATION_20 = (51, 204, 255, 255)
    MAGNIFICATION_30 = (52, 72, 255, 255)
    MAGNIFICATION_40 = (140, 0, 255, 255)

    ROI_COLORS = [MAGNIFICATION_MIN, MAGNIFICATION_2_5, MAGNIFICATION_5, MAGNIFICATION_10, MAGNIFICATION_20, MAGNIFICATION_30, MAGNIFICATION_40]
    ROI_LABELS = ["<2.5x", "2.5x - 5x", "5x - 10x", "10x - 20x", "20x - 30x", "30x - 40x", ">=40x"]

    def __init__(self, pixelCountX, pixelCountY, layer0X, layer0Y, scanMagnification, cellSize):
        self._grid = 0
        self._exportWidth = int(pixelCountX)
        self._exportHeight = int(pixelCountY)
        self._layer0X = int(layer0X)
        self._layer0Y = int(layer0Y)
        self.CELL_SIZE_X = int(cellSize)
        self.CELL_SIZE_Y = int(cellSize)
        self.SCAN_MAG = int(scanMagnification)

        self._gridHeight, self._gridWidth = self.calculateGridSize()

        # get font file
        if (not exists(self.FONT_FILE)):
            print("")
            print("#####################################################")
            print(f'# ERROR: no font file found at: {self.FONT_FILE} #')
            print("#####################################################")
            print("")
            exit()
        
        self._font = ImageFont.truetype(self.FONT_FILE, 100)

        # create 2D grid array for mapping gaze points
        self._grid = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

        # crete 2d grid array for mapping timestamp data
        self._gridTimestamps = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

        # create 2d grid array for hatching heatmap
        self._gridHatchingData = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]
        self.initGridHatchingData()

    # initialises grid with HatchingGridCell data
    def initGridHatchingData(self):
        for yCell in range(self._gridHeight):
            for xCell in range(self._gridWidth):
                self._gridHatchingData[yCell][xCell] = HGC()

    # runs the canny edge detection over the given image 
    # returns the result
    def getCannyImage(self, image, param1, param2):
        cannyImage = cv.cvtColor(np.array(image), cv.COLOR_BGR2GRAY)
        cannyImage = cv.Canny(cannyImage, threshold1=param1, threshold2=param2)
        cannyImage = Image.fromarray(cannyImage)

        newImage = Image.new('RGBA', (image.size[0], image.size[1]), color=(255, 255, 255, 255))
        newImage.paste(cannyImage)
        return newImage.copy()

    # calculates grid size
    def calculateGridSize(self):
        gridWidth = math.ceil(self._exportWidth / self.CELL_SIZE_X)
        gridHeight = math.ceil(self._exportHeight / self.CELL_SIZE_Y)

        # also add remainder
        leftoverX = self._exportWidth - (gridWidth * self.CELL_SIZE_X)
        gridWidth += math.ceil(leftoverX / self.CELL_SIZE_X)

        leftoverY = self._exportHeight - (gridHeight * self.CELL_SIZE_Y)
        gridHeight += math.ceil(leftoverY / self.CELL_SIZE_Y)

        return gridHeight, gridWidth

    # returns the calculated time spent on one wsi file
    # time is in seconds
    def getTimeSpentOnWSI(self, ImageSections):
        timeSpent = 0.0
        for imageSection in ImageSections:
            if (len(imageSection._timestamps) == 0):
                continue

            diff = imageSection._timestamps[-1] - imageSection._timestamps[0]
            timeSpent += diff
        
        timeSpent = timeSpent / 1000
        return int(timeSpent)  # round does not behave like expected

    # returns the magnification form the downsample factor
    def getMagnification(self, downsampleFactor):
        return self.SCAN_MAG / downsampleFactor

    # filters out invalid points
    # returns number of usable points
    def getValidGazepointCount(self, imageSection):
        counter = 0
        for gazePoints in imageSection._eyeTracking:
            # drop incomplete points
                if (self.incompleteGazeData(gazePoints)):
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoints)

                # check if mapped point is inside image section frame
                if (self.outsideImageSectionFrame(imageSection, gazePointX, gazePointY)):
                    continue
                
                counter += 1
        return counter

    # draws legend on bottom of the image to display start and end colors
    def addViewPathColorLegend(self, image, workerArgs):
        # draw legend, not high but as wide as image
        # merge both together. heatmap on top, legend on bottom
        heatmapWidth = image.size[0]
        legendHeight = int(image.size[1] * 0.1)

        legend = Image.new('RGBA', (heatmapWidth, legendHeight), (255, 255, 255))
        draw = ImageDraw.Draw(legend, 'RGBA')

        # make x offset 1% of width and drawHeight 30% of height
        offsetX = int(heatmapWidth * 0.01)
        drawHeight = int(legendHeight * 0.5)
        drawLine = int(drawHeight / 2)

        # need to load again to change size
        sizedFont = ImageFont.truetype(self.FONT_FILE, size=drawHeight)
        draw.text((offsetX, drawLine), "start", font=sizedFont, fill=(0, 0, 0))
        zeroWidth = sizedFont.getsize("start")[0]

        # draw end on the right side
        timeText = "end"
        textWidth = sizedFont.getsize(timeText)[0] + (2 * offsetX)
        draw.text((heatmapWidth - textWidth, drawLine), timeText, font=sizedFont, fill=(0, 0, 0))

        # make color gradient from left to right
        lineWidth = int(legendHeight * 0.7)

        # do this for x direction
        lineHeight = int(legendHeight / 2)
        startX = (2 * offsetX) + zeroWidth
        endX = heatmapWidth - startX - int(textWidth / 2)

        startColor = 0
        endColor = 0
        if (workerArgs._viewPathColorStart != 0):
            startColor = workerArgs._viewPathColorStart
        else:
            startColor = self.PATH_START_COLOR

        if (workerArgs._viewPathColorEnd != 0):
            endColor = workerArgs._viewPathColorEnd
        else:
            endColor = self.PATH_END_COLOR

        # TODO: cleanup and refactor (also in drawViewpathLegend)
        legendStep = 75
        for pixelX in range(startX, endX, legendStep):
            stepEnd = pixelX + legendStep - 1
            drawnPercentage = pixelX / endX

            # create color gradient
            R = int(endColor[0] * drawnPercentage + startColor[0] * (1 - drawnPercentage))
            G = int(endColor[1] * drawnPercentage + startColor[1] * (1 - drawnPercentage))
            B = int(endColor[2] * drawnPercentage + startColor[2] * (1 - drawnPercentage))
            A = 255

            draw.line(((pixelX, lineHeight), (stepEnd, lineHeight)), fill=(R, G, B, A), width=lineWidth)

        # now merge both
        totalHeight = image.size[1] + legendHeight
        heatmapLegend = Image.new('RGBA', (heatmapWidth, totalHeight))

        heatmapLegend.paste(image, (0, 0))
        heatmapLegend.paste(legend, (0, (image.size[1] + 1)))
        return heatmapLegend

    # draws view path with data from the eye tracker
    # returns base image with drawn on path
    def drawViewPath(self, baseImage, imageSections, workerArgs):
        image = baseImage.copy()
        viewPath = Image.new('RGBA', image.size, color=0)
        imageDraw = ImageDraw.Draw(viewPath, 'RGBA')
        lastPoint = None

        pointRadius = workerArgs._viewPathPointSize
        pathColorStart = workerArgs._viewPathColorStart
        pathColorEnd = workerArgs._viewPathColorEnd
        pathStrength = workerArgs._viewPathStrength
        pointColor = workerArgs._viewPathPointColor

        if (pointRadius == 0):
            pointRadius = self.POINT_RADIUS
        pointOffset = int(pointRadius / 2)

        drawnPoints = 0
        notDrawnPoints = 0
        incompletePonts = 0
        outsideFramePoints = 0
        for imageSection in imageSections:
            # just get point count and interpolate color over points
            drawnPointsCount = 0
            for gazePoints in imageSection._eyeTracking:

                # drop incomplete points
                if (self.incompleteGazeData(gazePoints)):
                    notDrawnPoints += 1
                    incompletePonts += 1
                    continue

                # map eye data to gaze point on output resolution image
                gazePointX, gazePointY = self.mapGazePoint(imageSection, gazePoints)

                # check if mapped point is inside image section frame
                if (self.outsideImageSectionFrame(imageSection, gazePointX, gazePointY)):
                    notDrawnPoints += 1
                    outsideFramePoints += 1
                    continue

                if (pointColor == 0):
                    pointColor = self.POINT_COLOR         

                # count how many points are drawable
                drawnPointsCount += 1
                pointSize = int(pointRadius)

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
                  width=pointSize)

            drawnPoints += drawnPointsCount
            #if imageSection._fileName == "MUGGRZ-PATH-SCAN-SS7525-1021032.svs":
            #    print(f'draw {drawnPointsCount} points | not drawn {notDrawnPoints} points | incomplete: {incompletePonts} | outside frame: {outsideFramePoints}')

        # now draw lines with clor gradient
        # need to draw start to end over all image sections
        # so calculate number of image sections and get number of points per image section to claculate percentage
        # this is no tperfectly efficcient to iterate and check all points twice...
        colorGradientCounter = 0
        newImage = True
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

                if (pathColorStart == 0):
                    pathColorStart = self.PATH_START_COLOR

                if (pathColorEnd == 0):
                    pathColorEnd = self.PATH_END_COLOR

                if (pathStrength == 0):
                    pathStrength = self.PATH_STRENGTH

                colorGradientCounter += 1

                drawnPercentage = colorGradientCounter / drawnPoints
                if (drawnPercentage > 1.0): # thats an error
                   print(f'drawnPercentage: {drawnPercentage}/1.0')

                pathColor = (
                   int(pathColorEnd[0] * drawnPercentage + pathColorStart[0] * (1 - drawnPercentage)),
                   int(pathColorEnd[1] * drawnPercentage + pathColorStart[1] * (1 - drawnPercentage)),
                   int(pathColorEnd[2] * drawnPercentage + pathColorStart[2] * (1 - drawnPercentage)),
                   int(pathColorEnd[3]))

                # if it is the first one we can't draw a line yet
                if (lastPoint is not None):
                   imageDraw.line([
                     (lastPoint[0], lastPoint[1]), (gazePointX, gazePointY)],
                     fill=pathColor,
                     width=pathStrength,
                     joint=None)

                if (newImage):
                    self.drawBiggerPoint(imageDraw, (gazePointX, gazePointY), pointSize, pathColorStart, 3)
                    newImage = False
                if (drawnPercentage == 1.0):
                    self.drawBiggerPoint(imageDraw, (gazePointX, gazePointY), pointSize, pathColorEnd, 3)

                lastPoint = (gazePointX, gazePointY)

        viewPath = Image.alpha_composite(image, viewPath)
        return viewPath

    # used for start and end point to be drawn bigger and in start/end path color
    def drawBiggerPoint(self, imageDraw, coordinates, pointRadius, pointColor, sizeFactor):
        pointSize = sizeFactor * pointRadius
        pointOffset = int(pointSize / 2)
        gazePointX = coordinates[0]
        gazePointY = coordinates[1]
        
        imageDraw.ellipse(
            [
                (gazePointX - pointOffset,
                gazePointY - pointOffset),
                (gazePointX + pointOffset,
                gazePointY + pointOffset)
            ],
            fill=pointColor,
            outline=None,
            width=pointSize)
        
        pointSize = pointRadius
        pointOffset = int(pointSize / 2)

    # returns roi legend drawn on bottom of roi image
    def addRoiColorLegend(self, image):
        heatmapWidth = image.size[0]
        cellNumber = len(self.ROI_LABELS)

        cellSizeHalf = 0
        if (self.CELL_SIZE_X < self.MIN_ROI_LEGEND_SIZE):
            cellSizeHalf = self.MIN_ROI_LEGEND_SIZE
        elif (self.CELL_SIZE_X > self.MAX_ROI_LEGEND_SIZE):
            cellSizeHalf = self.MAX_ROI_LEGEND_SIZE
        else:
            cellSizeHalf = int(self.CELL_SIZE_X / 2)

        legendHeight = int(image.size[1] * 0.1) + (2*cellSizeHalf)

        legend = Image.new('RGBA', (heatmapWidth, legendHeight), color=(255, 255, 255))
        draw = ImageDraw.Draw(legend, 'RGBA')

        # draw one "cell" with color and underneath the "zoom" rating
        offsetX = int(heatmapWidth / (cellNumber + 1))
        drawHeight = int(legendHeight * 0.3)

        # need to load again to change size
        sizedFont = ImageFont.truetype(self.FONT_FILE, size=drawHeight)

        for i in range(0, cellNumber):
            startX = offsetX * (i + 1)
            draw.rectangle(
              (startX - cellSizeHalf, drawHeight - cellSizeHalf, startX + cellSizeHalf, drawHeight + cellSizeHalf),
              fill=None,
              outline=self.ROI_COLORS[i],
              width=10)

            fontWidth, _ = draw.textsize(self.ROI_LABELS[i], sizedFont)
            fontWidthOffset = startX - int(fontWidth / 2)

            draw.text((fontWidthOffset, drawHeight + (legendHeight * 0.2)), self.ROI_LABELS[i], font=sizedFont, fill=(0, 0, 0))

        totalHeight = image.size[1] + legendHeight
        heatmapLegend = Image.new('RGBA', (heatmapWidth, totalHeight))
        heatmapLegend.paste(image, (0, 0))
        heatmapLegend.paste(legend, (0, (image.size[1] + 1)))
        return heatmapLegend

    # returns legend drawing on bottom of heatmap

    def addHeatmapColorLegend(self, image, ImageSections):
        legendStep = 75

        # draw legend, not high but as wide as image
        # merge both together. heatmap on top, legend on bottom
        heatmapWidth = image.size[0]
        legendHeight = int(image.size[1] * 0.1)

        legend = Image.new('RGBA', (heatmapWidth, legendHeight), (255, 255, 255))
        draw = ImageDraw.Draw(legend, 'RGBA')
        
        # draw start on left side
        offsetX = int(heatmapWidth * 0.01)
        drawHeight = int(legendHeight * 0.5)
        drawLine = int(drawHeight / 2)

        # need to load again to change size
        sizedFont = ImageFont.truetype(self.FONT_FILE, size=drawHeight)
        draw.text((offsetX, drawLine), "0.0", font=sizedFont, fill=(0, 0, 0))
        zeroWidth = sizedFont.getsize("0.0")[0]

        # draw end on the right side
        timeSpent = self.getTimeSpentOnWSI(ImageSections)
        timeText = " | total time: " + str(timeSpent) + " seconds"
        textWidth = sizedFont.getsize(timeText)[0] + 80
        draw.text((heatmapWidth - textWidth, drawLine), timeText, font=sizedFont, fill=(0, 0, 0))
        oneWidth = sizedFont.getsize("1.0")[0]
        oneOffset = heatmapWidth - textWidth - oneWidth - offsetX - 30
        draw.text((oneOffset, drawLine), "1.0", font=sizedFont, fill=(0, 0, 0))

        # make color gradient from left to right
        lineWidth = int(legendHeight * 0.7)

        # do this for every x pixel
        lineHeight = int(legendHeight / 2)
        startX = (2 * offsetX) + zeroWidth
        endX = heatmapWidth - startX - textWidth - oneWidth

        for pixelX in range(startX, endX + 1, legendStep):
            stepEnd = pixelX + legendStep - 1

            # create color gradient
            colorX = (pixelX - startX) / (endX - startX)

            A = (int(255 * colorX))
            B = 205
            G = 244
            R = 50
            draw.line(((pixelX, lineHeight), (stepEnd, lineHeight)), fill=(R, G, B, A), width=lineWidth)

        # now merge both
        totalHeight = image.size[1] + legendHeight
        heatmapLegend = Image.new('RGBA', (heatmapWidth, totalHeight))

        heatmapLegend.paste(image, (0, 0))
        heatmapLegend.paste(legend, (0, (image.size[1] + 1)))

        return heatmapLegend

    # draws hatching onto a given .jpg
    # returns image with hatched cell tiles
    def getHatchingHeatmap(self, baseImage, imageSections, alpha):
        image = baseImage.copy()
        hatching = Image.new('RGBA', image.size, color=0)

        # see how much time someone has spent looking on one grid cell
        for imageSection in imageSections:
            # time is in ms
            timeSpent = 0.0
            if (len(imageSection._timestamps) >= 1):
                timeSpent = imageSection._timestamps[-1] - imageSection._timestamps[0]

            # create a grid for every image section
            imageSectionTimestamps = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

            # additional grid to save magnification factors
            gridMagnificationFactors = [[0.0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

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

                magnificationFactor = self.getMagnification(imageSection._downsampleFactor)

                # print overlapping hatching instead of just max "values"
                self._gridHatchingData[yCell][xCell].setHatchingFlag(
                    imageSectionTimestamps[yCell][xCell],
                    magnificationFactor)

                # now save it as magnification
                #if (imageSection._downsampleFactor > gridMagnificationFactors[yCell][xCell]):
                if (magnificationFactor > gridMagnificationFactors[yCell][xCell]):
                    gridMagnificationFactors[yCell][xCell] = magnificationFactor

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
        heatmap = self.drawHatchingData(hatching, alpha)
        smth = Image.alpha_composite(image, heatmap)
        return smth

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

    # draws hatching with complex data
    def drawHatchingData(self, image, alpha):
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
                
                for key in self._gridHatchingData[yCell][xCell].getKeys():
                    gotCurrentFlag = self._gridHatchingData[yCell][xCell].getHatchingFlag(key)

                    #hatchingPattern = hatching.getDefautlHatching()
                    if (gotCurrentFlag):
                        hatchingPattern = hatching.getHatching(key)
                        image.paste(hatchingPattern, (cellCenterX, cellCenterY), hatchingPattern)
        return image

    # returns image with drawn on hatching
    def drawHatching(self, image, grid, gridMagnificationFactors, alpha=230):
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
                hatchingPattern = hatching.getHatching(grid[yCell][xCell], gridMagnificationFactors[yCell][xCell])
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

    # maps a given value to a specifyed range
    def mapValue(self, value, minInput, maxInput, minOutput, maxOutput):
        return (value - minInput)/(maxInput - minInput) * (maxOutput - minOutput) + minOutput

    # draws the Image Sections (ROI) on the extracted wsi layer
    # parts of this code is from Markus
    # returns wsi image with rectangle on it
    def drawRoiOnImage(self, baseImage, imageSections, filling=None, lineWidth=10):
        alphaImage = baseImage.copy()
        alphaImage.load() # needed for split()

        image = Image.new('RGB', alphaImage.size, (255, 255, 255))
        image.paste(alphaImage, mask=alphaImage.split()[3]) # 3 is alpha

        draw = ImageDraw.Draw(image, 'RGBA')

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

            # check magnification and draw lines in corresponding colors
            magnification = self.getMagnification(imageSection._downsampleFactor)
            outlineColor = (0, 0, 0)

            if (magnification < 2.5):
                outlineColor = self.MAGNIFICATION_MIN

            elif (magnification >= 2.5 and magnification < 5):
                outlineColor = self.MAGNIFICATION_2_5
            
            elif (magnification >= 5 and magnification < 10):
                outlineColor = self.MAGNIFICATION_5

            elif (magnification >= 10 and magnification < 20):
                outlineColor = self.MAGNIFICATION_10

            elif (magnification >= 20 and magnification < 30):
                outlineColor = self.MAGNIFICATION_20

            elif (magnification >= 30 and magnification < 40):
                outlineColor = self.MAGNIFICATION_30

            elif (magnification > 40 and magnification >= 30):
                outlineColor = self.MAGNIFICATION_40

            rawAlpha = 100 * normalizedList[index]
            scaledAlpha = self.mapValue(rawAlpha, 0.0, 100.0, (self.MIN_ROI_ALPHA * 255), 255)

            outlineing=(
              outlineColor[0],
              outlineColor[1],
              outlineColor[2],
              int(scaledAlpha))

            draw.rectangle((
                topLeftX,
                topLeftY,
                bottomRightX,
                bottomRightY),
                fill=filling,
                outline=outlineing,
                width=lineWidth)

            # for debug only
            #draw.ellipse([(topLeftX, topLeftY), (topLeftX + 5, topLeftY + 5)], outline="black", fill="black")
            #draw.ellipse([(bottomRightX - 5, bottomRightY - 5), (bottomRightX, bottomRightY)], outline="red", fill="red")
        return image

    # extracts a "level" (only resolution) of the whole slide image and converts it to a image
    # returns the level on success or None on failure
    def extractThumbnail(self, slide, wsiDict, wsiName):
        wsiDict[wsiName] = slide.get_thumbnail((self._exportWidth, self._exportHeight))

    # wrapper for drawGridValues.
    # returns color map of given image
    def getColorMap(self, image, gridValues):
        colorMap = Image.new('RGBA', image.size, color=(0,0,0,255))
        return self.drawGridValues(colorMap, gridValues, 255)
    
    # wrapper for drawGridValues
    # returns color grid on given image
    def drawColorHeatmap(self, image, gridValues):
        return self.drawGridValues(image, gridValues, 0)

    # turns grid values into cell colors and draws them on given image
    # grid values need to be normalized first!
    # returns drawing on image
    def drawGridValues(self, image, gridValues, defaultAlpha):
        image = Image.new('RGBA', image.size, color=(0, 0, 0, defaultAlpha))
        draw = ImageDraw.Draw(image, 'RGBA')
        # [width, height] (for all rows make the columns)
        gridColors = [[0 for x in range(self._gridWidth)] for y in range(self._gridHeight)]

        # first get through array of values to make array of colors
        for yCell in range(self._gridHeight):
            for xCell in range(self._gridWidth):
                cellValue = gridValues[yCell][xCell]
                A = defaultAlpha
                B = 0
                G = 0
                R = 0

                if (cellValue != 0.0):
                    A = (int(255 * cellValue))
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
        # falsch!
        deadWidth = self.DISPLAY_X - imageSection._width
        deadHeight = self.DISPLAY_Y - imageSection._height

        #if deadHeight < 0 or deadWidth < 0:
        #    print("dead height/width is negative")

        # current height, current width are relative to wsi
        # calculate gaze point relative to frame. image section is shown on monitor
        # within iMotions window (just nearby dead window part)
        # falsch!
        print(f'{gazeX} - {deadWidth} = {gazeX - deadWidth}')
        relativeGazePointX = gazeX - deadWidth
        relativeGazePointY = gazeY - deadHeight

        #if relativeGazePointX < 0 or relativeGazePointY < 0:
        #    print("relative gaze point is negative")

        # next step is to calculate gaze point position relative to wsi
        # image section corner points (view roi) are relative to wsi so use them
        realGazeX = imageSection._topLeftX + relativeGazePointX
        realGazeY = imageSection._topLeftY + relativeGazePointY

        #if realGazeX < 0 or realGazeY < 0:
        #    print("real gaze is negative")

        # now map gaze points to export resolution
        resolutionFactorX = self._exportWidth / self._layer0X
        resolutionFactorY = self._exportHeight / self._layer0Y

        #if resolutionFactorX < 0 or relativeGazePointY < 0:
        #    print("negative resolution factor")

        exportGazeX = int(realGazeX * resolutionFactorX)
        exportGazeY = int(realGazeY * resolutionFactorY)

        # this should be it

        return (exportGazeX, exportGazeY) # why are some indexes negative?

    # try to rewrite mapGazePoint but in a more correct manner
    def mapGazePointCorrect(self, imageSection, gazePoints):
        gazeX = int((gazePoints._leftX + gazePoints._rightX) / 2)
        gazeY = int((gazePoints._leftY + gazePoints._rightY) / 2)


        pass

    # returns mapped Cell on grid [x, y]
    def mapToCell(self, gazeX, gazeY):
        xCell = math.floor(gazeX / self.CELL_SIZE_X)
        yCell = math.floor(gazeY / self.CELL_SIZE_Y)
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
    # returns colored, mostly transparent, cells rendered onto a .png
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
        heatmap = self.drawColorHeatmap(image, normalizedGridData)
        colorMap = self.getColorMap(image, normalizedGridData)
        return (Image.alpha_composite(baseImage, heatmap), colorMap)
