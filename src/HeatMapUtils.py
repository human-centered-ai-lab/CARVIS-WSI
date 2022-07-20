# HeatMapUtils

''' holds all functionallity which is used for drawing the heatmaps '''

# a fine grid needs to be layed over the image. when an eyeData point
# hits a grid cell, it's counter will be increased. then the grid will get
# colorised according to it cell's hit rate and displayed over the original
# wsi image layer.
#
# all eyeData points need to be calculated back to the original image pixels at level 0.
# data for this is in each corresponding ImageSection.

from PIL import Image, ImageDraw

class HeatMapUtils():
    CELL_SIZE_X = 100
    CELL_SIZE_Y = 100

    def __init__(self, pixelCountX, pixelCountY):
        self._grid = 0

        xCells = pixelCountX // self.CELL_SIZE_X
        yCells = pixelCountY // self.CELL_SIZE_Y
        
        self._grid = [[self._grid for i in range(xCells)] for j in range(yCells)]

    # draws the path of eyes on the wsi extracted layer
    # returns wsi layer with path drawing on it
    def drawViewPath(self, image, viewPoints, color, lineThicknes):
        pass

    # draws the Image Sections (ROI) on the extracted wsi layer
    # returns wsi image with rectangle on it
    def drawRoiOnImage(self, image, imageSections, filling=None, outlineing=('#9EFF00'), lineWidth=3):
        draw = ImageDraw.Draw(image, "RGBA") # (200, 100, 0, 5) | '#9EFF00'

        # do this for all image sections
        for imageSection in imageSections:
            topLeftX = int(float(imageSection._topLeftX))
            topLeftY = int(float(imageSection._topLeftY))
            bottomRightX = int(float(imageSection._bottomRightX))
            bottomRightY = int(float(imageSection._bottomRightY))

            #print(f'{topLeftX} {topLeftY} {bottomRightX} {bottomRightY}')

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
    def extractLayer(self, slide, level):
        if (level > slide.level_count or level < 0):
            print("Requested level is not supported!")
            return None
        
        dimensions = slide.level_dimensions[level]
        return slide.get_thumbnail((dimensions[0], dimensions[1]))  # this does run like forever in lower levels

    # calculates the "heat" of a grid cell by increasing the cells counter by 1
    # every thime the eyeData hits a cell
    def calculateActivityValue(self):
        # add 1 to every matrix cell where eyeData fits the cell
        pass

    # calculates on how many pixels the grid does overshoot
    # if returned pixels are < 0 the grid is bigger than the wsi in layer 0
    # if the returned pixels are > 0 the grid is smaller than whe wsi in layer 0
    # returns tuple (x, y) of pixels
    #def getUndefinedPixels(self, slide):
    #    overshootX = (self._pixelPerCellX * self.GRID_SIZE_X) - slide.dimensions[0]
    #    overshootY = (self._pixelPerCellY * self.GRID_SIZE_Y) - slide.dimensions[1]
    #    return (overshootX, overshootY)
    