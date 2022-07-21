# HeatMapUtils

''' holds all functionallity which is used for drawing the heatmaps '''

# a fine grid needs to be layed over the image. when an eyeData point
# hits a grid cell, it's counter will be increased. then the grid will get
# colorised according to it cell's hit rate and displayed over the original
# wsi image layer.
#
# all eyeData points need to be calculated back to the original image pixels at level 0.
# data for this is in each corresponding ImageSection.

from PIL import Image, ImageDraw, ImageFont

class HeatMapUtils():
    CELL_SIZE_X = 100
    CELL_SIZE_Y = 100
    SCREEN_SIZE_X = 1920
    SCREEN_SIZE_Y = 1080

    def __init__(self, pixelCountX, pixelCountY):
        self._grid = 0
        self.extractedSizeX = int(pixelCountX)
        self.extractedSizeY = int(pixelCountY)

        print(self.extractedSizeX)

        xCells = self.extractedSizeX // self.CELL_SIZE_X
        yCells = self.extractedSizeY // self.CELL_SIZE_Y

        self._grid = [[self._grid for i in range(xCells)] for j in range(yCells)]

    # code is from Markus
    # draws a legend on lefty upper corner for the sample rate
    # returns image with drawn on legend
    def drawLegend(self, image):
        draw = ImageDraw.Draw(image, "RGBA")

        # draw samplerates and colors
        font = ImageFont.truetype("arial.ttf", 100)
        draw.rectangle((0, 0, 800, 100), fill=(204,255,51, 255),width=25)
        draw.text((0, 0),"Downsample <1",(0,0,0), font = font)
        draw.rectangle((0, 100, 800, 200), fill=(102,255,51, 255),width=25)
        draw.text((0, 100),"Downsample <4",(0,0,0), font = font)
        draw.rectangle((0, 200, 800, 300), fill=(51,255,102, 255),width=25)
        draw.text((0, 200),"Downsample <10",(0,0,0), font = font)
        draw.rectangle((0, 300, 800, 400), fill=(51,255,204, 255),width=25)
        draw.text((0, 300),"Downsample <20",(0,0,0), font = font)
        draw.rectangle((0, 400, 800, 500), fill=(51,204,255, 255),width=25)
        draw.text((0, 400),"Downsample <30",(0,0,0), font = font)
        draw.rectangle((0, 500, 800, 600), fill=(51,102,255, 255),width=25)
        draw.text((0, 500),"Downsample <40",(0,0,0), font = font)
        draw.rectangle((0, 600, 800, 700), fill=(102,51,255, 255),width=25)
        draw.text((0, 600),"Downsample >40",(0,0,0), font = font)
        
        return image

    # draws the path of eyes on the wsi extracted layer
    # returns wsi layer with path drawing on it
    def drawViewPath(self, image, viewPoints, color, lineThicknes):
        # ToDo
        pass

    # draws the Image Sections (ROI) on the extracted wsi layer
    # parts of this code is from Markus
    # returns wsi image with rectangle on it
    def drawRoiOnImage(self, image, imageSections, filling=None, lineWidth=10):
        draw = ImageDraw.Draw(image, "RGBA") # (200, 100, 0, 5) | '#9EFF00'

        # do this for all image sections
        for imageSection in imageSections:
            topLeftX = int(float(imageSection._topLeftX))
            topLeftY = int(float(imageSection._topLeftY))
            bottomRightX = int(float(imageSection._bottomRightX))
            bottomRightY = int(float(imageSection._bottomRightY))

            sampleFactor = int(float(imageSection._downsampleFactor))
            outlineing=(100,200,0, 10)

            if sampleFactor < 1:
                outlineing = (204,255,51, 10)
            elif sampleFactor < 4:
                outlineing = (102,255,51, 10)
            elif sampleFactor < 10:
                outlineing = (51,255,102, 10)
            elif sampleFactor < 20:
                outlineing = (51,255,204, 10)
            elif sampleFactor < 30:
                outlineing = (51,204,255, 10)
            elif sampleFactor < 40:
                outlineing = (51,102,255, 10)
            else:
                outlineing = (102,51,255, 10)

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

    # calculates the "heat" of a grid cell by increasing the cells counter by 1
    # every time the eyeData's gaze point hits a cell
    def calculateActivityValues(self, image, imageSections):
        # go through all image sections
        # go through all eyeData and calculate eye position according to image section frame
        # check if position is in picture frame
        # add 1 to every matrix cell where eyeData fits the cell

        for imageSection in imageSections:
            # image section scale factor
            for eyeGazePosition in imageSection._eyeTracking[0]:
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

    # calculates on how many pixels the grid does overshoot
    # if returned pixels are < 0 the grid is bigger than the wsi in layer 0
    # if the returned pixels are > 0 the grid is smaller than whe wsi in layer 0
    # returns tuple (x, y) of pixels
    #def getUndefinedPixels(self, slide):
    #    overshootX = (self._pixelPerCellX * self.GRID_SIZE_X) - slide.dimensions[0]
    #    overshootY = (self._pixelPerCellY * self.GRID_SIZE_Y) - slide.dimensions[1]
    #    return (overshootX, overshootY)
    