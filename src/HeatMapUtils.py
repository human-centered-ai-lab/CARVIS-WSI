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

    def __init__(self, pixelCountX, pixelCountY):
        self._grid = 0
        self.extractedSizeX = int(pixelCountX)
        self.extractedSizeY = int(pixelCountY)

        print(f'image width/height ratio: {self.extractedSizeX/self.extractedSizeY}')

        self.xCells = math.ceil(self.extractedSizeX / self.CELL_SIZE_X)
        self.yCells = math.ceil(self.extractedSizeY / self.CELL_SIZE_Y)
        print(f'grid width/height ratio: {self.xCells/self.yCells}')

        # create 2D grid [array] for mapping heat
        # [height, width] (for all rows make the columns)
        self._grid = [[self._grid for i in range(self.yCells)] for j in range(self.xCells)]
        print(f'grid size [width/height]: {len(self._grid)} {len(self._grid[0])}')

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
        normalizedGrid = [[self._grid for i in range(len(self._grid[0]))] for j in range(len(self._grid))]
        minValue = sys.maxsize
        maxValue = 0

        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                if (self._grid[i][j] > maxValue):
                    maxValue = self._grid[i][j]
                if (self._grid[i][j] < minValue):
                    minValue = self._grid[i][j]

        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                x = self._grid[i][j]
                normalizedGrid[i][j] = (x- minValue) / (maxValue - minValue)

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
        # [height, width] (for all rows make the columns)
        gridColors = [[gridValues for i in range(len(gridValues[0]))] for j in range(len(gridValues))]

        # first get through array of values to make array of colors
        for yCell in range(len(gridValues[0])):
            for xCell in range(len(gridValues)):
                A = 50
                B = int(255 * gridValues[xCell][yCell])
                G = int(255 * (1 - gridValues[xCell][yCell]))
                R = 0
                gridColors[xCell][yCell] = (A, R, G, B)

        # go through all grid cells and get the center position on the image
        for xCell in range(len(gridValues)):
            for yCell in range(len(gridValues[xCell])):
                # map the cell to an image pixel coordinate
                pixelX = xCell * self.CELL_SIZE_X
                pixelY = yCell * self.CELL_SIZE_Y
                pixelXEnd = pixelX + 100
                pixelYEnd = pixelY + 100

                if (pixelX > self.extractedSizeX or pixelXEnd > self.extractedSizeX):
                    continue

                if (pixelY > self.extractedSizeY or pixelYEnd > self.extractedSizeY):
                    continue
                
                # position calculation does not work like that!
                # or grid size must be recalculated
                A = gridColors[xCell][yCell][0]
                R = gridColors[xCell][yCell][1]
                G = gridColors[xCell][yCell][2]
                B = gridColors[xCell][yCell][3]
                draw.rectangle((pixelX+10, pixelY+10, pixelXEnd-10, pixelYEnd-10), fill=(R, G, B, A), width=1)

        # draw there a point of calculated color
        return image

    # calculates heat of grid cells which stretch over an image
    # maps eyeData coordinates onto the grid cells. each hit increases the heat of the cell
    # returns colored (but transparent) cells rendered onto a .jpg
    # parts of this code is from Markus Plass
    def getHeatmap(self, image, imageSections):
        # https://stackoverflow.com/questions/9816024/coordinates-to-grid-box-number
        # https://stackoverflow.com/questions/20368413/draw-grid-lines-over-an-image-in-matplotlib

        for imageSection in imageSections:
            for eyeData in imageSection._eyeTracking:

                # if incomplete data -> drop datapoint
                if (eyeData._gazeLeftX < 0
                  or eyeData._gazeRightX < 0
                  or eyeData._gazeLeftY < 0
                  or eyeData._gazeRightY < 0):
                    continue

                # check if eye gaze point is inside display area of image section
                # (=inside iMotions window)
                gazePointX = int((eyeData._gazeLeftX + eyeData._gazeRightX) / 2)
                gazePointY = int((eyeData._gazeLeftY + eyeData._gazeRightY) / 2)

                posXBottomRight = self.DISPLAY_X - gazePointX
                posYBottomRight = self.DISPLAY_Y - gazePointY

                # when eye gaze point is not inside image section -> drop datapoint
                if (posXBottomRight >= imageSection._width and posYBottomRight <= imageSection._height):
                    continue

                '''# rethink this part of the code...   without is better
                # calculate exect eye gaze point
                #gazePointX = imageSection._bottomRightX - posXBottomRight * imageSection._downsampleFactor
                #gazePointY = imageSection._bottomRightY - posYBottomRight * imageSection._downsampleFactor

                #gazePointX = gazePointX / imageSection._downsampleFactor
                #gazePointY = gazePointY / imageSection._downsampleFactor'''

                # new approach for calculating gaze point
                gazePointX = int((eyeData._gazeLeftX + eyeData._gazeRightX) / 2)
                gazePointY = int((eyeData._gazeLeftY + eyeData._gazeRightY) / 2)

                # check if gaze point is inside image section frame
                if (gazePointX > imageSection._bottomRightX and not gazePointX < 0):
                    continue
                if (gazePointY > imageSection._bottomLeftY and not gazePointY < 0):
                    continue

                # map gaze point to image pixel coordinates
                print(gazePointX * imageSection._downsampleFactor)

                print(f'gaze point [x,y] {gazePointX, gazePointY} [width,height]: {imageSection._width, imageSection._height} sampleFactor: {imageSection._downsampleFactor}')


                # now map gazePoint to grid cell
                # - 1 because we need index
                xCell = math.ceil((gazePointX / self.xCells)) - 1
                yCell = math.ceil((gazePointY / self.yCells)) - 1

                #print(f'x: {xCell} y: {yCell} | xCells: {self.xCells} yCells: {self.yCells}')

                self._grid[yCell][xCell] += 1
        
        # normalize grid data
        normalizedGridData = self.normalizeGridData()
        
        # draw grid values on image and return
        return self.drawGridValues(image, normalizedGridData)

    # calculates the "heat" of a grid cell by increasing the cells counter by 1
    # every time the eyeData's gaze point hits a cell
    def calculateActivityValues(self, image, imageSections):
        # go through all image sections
        # go through all eyeData and calculate eye position according to image section frame
        # check if position is in picture frame
        # add 1 to every matrix cell where eyeData fits the cell

        for imageSection in imageSections:
            # image section scale factor
            for eyeGazePosition in imageSection._eyeTracking:
                # check if something is saved before converting
                if (eyeGazePosition._gazeLeftX == ''
                or eyeGazePosition._gazeLeftY == ''
                or eyeGazePosition._gazeRightX == ''
                or eyeGazePosition._gazeRightY == ''):
                        continue

                # check if eye position was tracked
                if (not int(float(eyeGazePosition._gazeLeftX)) > -1
                or not int(float(eyeGazePosition._gazeLeftY)) > -1
                or not int(float(eyeGazePosition._gazeRightX)) > -1
                or not int(float(eyeGazePosition._gazeRightY)) > -1):
                        continue

                gazeLeftX = int(float(eyeGazePosition._gazeLeftX))
                gazeLeftY = int(float(eyeGazePosition._gazeLeftY))
                gazeRightX = int(float(eyeGazePosition._gazeRightX))
                gazeRightY = int(float(eyeGazePosition._gazeRightY))

                # calc eye position
                eyePositionX = int((gazeLeftX + gazeRightX) / 2)
                eyePositionY = int((gazeLeftY + gazeRightY) / 2)

                # take image section sample factor into account
                eyePositionX = int(float(eyePositionX) * float(imageSection._downsampleFactor))
                eyePositionY = int(float(eyePositionY) * float(imageSection._downsampleFactor))

                # map grid cells to image positoins to make the counter thing working


                # until this works now: draw point on image
                draw = ImageDraw.Draw(image, "RGBA")
                #draw.point((eyePositionX, eyePositionY), fill=(100,200,0, 10))
                draw.ellipse([(eyePositionX-4, eyePositionY-4), (eyePositionX+4, eyePositionY+4)], fill=('#00cc00'), width=20)

        return image
    