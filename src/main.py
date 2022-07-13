#!/usr/bin/python3

''' 
main.py
draws heatmap of eye tracking on jpeg extraction of whole slide image
'''

# ToDo:
#
# - openslide does bad things when calling read_region, 
# (- add more string testing for image section parameters?)
#

import os
import sys
import csv
from os.path import exists
from ImageSection import ImageSection
from EyeData import EyeData
from HeatMapUtils import HeatMapUtils
from PIL import Image
from openslide import open_slide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

ROI_CHANGE_SIGNAL = "%7b%22"
wsiLevel = 0

# options/settings via terminal args
# extract images, and save with heatmaps overlay and viewpath
# datapoints: eye tracking data is viewport specific

# usage: main.py <CSV File> <SVS FILE> <EXTRACTION LAYER>

# extracts the eye tracking data for all image sections
# returns: list of imageSections
def extractImageSections():
    pass

# reds csv and returns a dictionary with headlines as keys
def readCSV(file):
    ImageSectionList = []
    eyeDataList = []

    with open(file, newline='') as csvfile:
        csvFile = csv.reader(csvfile, delimiter=',')

        # sort data by ImageSections
        readOK = False
        imageSectionTimestamps = []

        for row in csvFile:
            if (row[0] == '1'): # line after "Row"
                readOK = True
                continue
            
            # in first line where timestamps are
            if (readOK):
                roiChangeColumn = row[11][:6]

                # initializing first image section
                # this does not have image section parameters,
                # so it only has "standard" values
                # -> user has not changed roi since start of the session
                if not ImageSectionList:
                    ImageSectionList.append(ImageSection(
                      "None",
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0
                    ))

                # until there is a new signal for roi change, save all eye tracking values
                # in eyeDataList and insert it to the existing and currently active image 
                # section (last one in ImageSectionList)
                if (roiChangeColumn != ROI_CHANGE_SIGNAL):
                    eyeDataList.append(EyeData(
                      row[17],
                      row[18],
                      row[19],
                      row[20],
                      row[21],
                      row[22],
                      row[23],
                      row[24],
                      row[25]))
                    
                    imageSectionTimestamps.append(row[1])

                # when there is a new roi change signal save all currently
                # collected data to existing image section and create a new one
                if (roiChangeColumn == ROI_CHANGE_SIGNAL):
                    ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
                    ImageSectionList[-1].addEyeTracking(eyeDataList)

                    # after adding collected eye tracking data to corresponding image section
                    # clear the list so the next image section gets only its eye data
                    imageSectionTimestamps.clear()
                    eyeDataList.clear()

                    # now initialise a new ImageSection
                    # first get all needed parameters from the roi change string
                    roiChangeString = row[11]
                    nameStart = roiChangeString.find("Filename")
                    
                    if(nameStart == -1):
                        print("Something has gone terribly wrong. ROI change string has no Filename!")
                        exit()
                    
                    nameStart += 17 # offset for Filename%22%3a%22
                    nameEnd = roiChangeString.find(".svs")
                    nameEnd += 4 # offset for .svs

                    fileName = roiChangeString[nameStart : nameEnd]

                    # center x
                    centerXStart = roiChangeString.find("CurrentCenterX")
                    centerXStart += 20
                    centerXEnd = roiChangeString.find("CurrentCenterY")
                    centerXEnd -= 6

                    centerX = roiChangeString[centerXStart : centerXEnd]

                    # center y
                    centerYStart = roiChangeString.find("CurrentCenterY")
                    centerYStart += 20
                    centerYEnd = roiChangeString.find("CurrentDownsampleFactor")
                    centerYEnd -= 6

                    centerY = roiChangeString[centerYStart : centerYEnd]

                    # sample factor
                    sampleFactorStart = roiChangeString.find("CurrentDownsampleFactor")
                    sampleFactorStart += 29
                    sampleFactorEnd = roiChangeString.find("Width")
                    sampleFactorEnd -= 6

                    sampleFactor = roiChangeString[sampleFactorStart : sampleFactorEnd]

                    # width
                    widthStart = roiChangeString.find("Width")
                    widthStart += 11
                    widthEnd = roiChangeString.find("Height")
                    widthEnd -= 6

                    width = roiChangeString[widthStart : widthEnd]

                    # height

                    # now a new tmp substring is needed since there are 
                    # some parameters more than once in this string and otherwise
                    # and find only returns the location of the first appearance
                    # of a searched substring
                    roiChangeSubstring = roiChangeString[widthEnd:]
                    heightStart = roiChangeSubstring.find("Height")
                    heightStart += 12
                    heightEnd = roiChangeSubstring.find("CurrentCenterY")
                    heightEnd -= 6

                    height = roiChangeSubstring[heightStart : heightEnd]

                    # roi
                    roiStart = roiChangeSubstring.find("ViewROI")
                    roiStart += 7
                    roiEnd = roiChangeSubstring.find("TopLeft")

                    roi = roiChangeSubstring[roiStart : roiEnd]

                    # top left - there may be a second parameter leftover
                    topLeftStart = roiChangeSubstring.find("TopLeft")
                    topLeftStart += 26
                    topLeftEnd = roiChangeSubstring.find("TopRight")
                    topLeftSubstring = roiChangeSubstring[topLeftStart : topLeftEnd]
                    topLeftEnd = topLeftSubstring.find("%2c%22")

                    topLeft = topLeftSubstring[: topLeftEnd]

                    # top right - there may be a second parameter leftover
                    topRightStart = roiChangeSubstring.find("TopRight")
                    topRightStart += 27
                    topRightEnd = roiChangeSubstring.find("BottomLeft")
                    topRightSubstring = roiChangeSubstring[topRightStart : topRightEnd]
                    topRightEnd = topRightSubstring.find("%2c%22")

                    topRight = topRightSubstring[: topRightEnd]

                    # bottom left - there may be a second parameter leftover
                    bottomLeftStart = roiChangeSubstring.find("BottomLeft")
                    bottomLeftStart += 29
                    bottomLeftEnd = roiChangeSubstring.find("BottomRight")
                    bottomLeftSubstring = roiChangeSubstring[bottomLeftStart : bottomLeftEnd]
                    bottomLeftEnd = bottomLeftSubstring.find("%2c%22")

                    bottomLeft = bottomLeftSubstring[: bottomLeftEnd]

                    # bottom right - there may be a second parameter leftover
                    bottomRightStart = roiChangeSubstring.find("BottomRight")
                    bottomRightStart += 30
                    bottomRightSubstring = roiChangeSubstring[bottomRightStart :]
                    bottomtRightEnd = bottomRightSubstring.find("%2c%22")

                    bottomRight = bottomRightSubstring[: bottomtRightEnd]

                    ImageSectionList.append(ImageSection(
                      fileName,
                      centerX,
                      centerY,
                      sampleFactor,
                      width,
                      height,
                      roi,
                      topLeft,
                      topRight,
                      bottomLeft,
                      bottomRight
                      ))

        # also don't forget to save all pending eye tracking data
        ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
        ImageSectionList[-1].addEyeTracking(eyeDataList)

        imageSectionTimestamps.clear()
        eyeDataList.clear()

        return ImageSectionList

# checks if the user choosen input makes sense
def verifyInput():
    if (len(sys.argv) != 4):
        terminate()

    if not exists(sys.argv[1]):
        print("File not found!")
        terminate()
    
    if not os.path.exists(sys.argv[2]):
        print("given data directory does not exist!")
        print("Note that the directory parameter must be relative to your current path.")
        terminate()
    
    wsiLevel = sys.argv[3]

# prints usage and exits
def terminate():
    print("usage: main.py <CSV FILE> <SVS DIRECTORY> <EXTRACTION LAYER>")
    exit()

# reads the svs file and extracs the needed
def readSVS(file):
    if not exists(file):
        print(f'The needed wsi file {file} does not exist!')
        terminate()

    wsiSlide = open_slide(file)
    print(f'reqested Image filename: {file}')
    print(f'slide level count: {wsiSlide.level_count} level dimensions: {wsiSlide.level_dimensions}')
    return wsiSlide

if __name__ == "__main__":
    verifyInput()

    csvData = readCSV(sys.argv[1])

    wsiFileName = csvData[1]._fileName
    print(f'real filename: {wsiFileName}')
    wsiSlide = readSVS(sys.argv[2] + wsiFileName)

    dims = wsiSlide.level_dimensions
    heatMapUtils = HeatMapUtils(dims[wsiLevel][0], dims[wsiLevel][1])

    img = heatMapUtils.extractLayer(wsiSlide, 3)
    img.show()

    #print(f'{heatMapUtils._pixelPerCellX}, {heatMapUtils._pixelPerCellY}')
    print(f'pixels per cell [x, y]: {heatMapUtils._pixelPerCellX}, {heatMapUtils._pixelPerCellY}')

    # a fine grid needs to be layed over the image. when an eyeData point will
    # hit one grid cell, it's counter will be increased. then the grid will get
    # colorised according to it cell's hit rate and displayed over the original
    # wsi image layer.
    #
    # all eyeData points need to be calculated back to the original image pixels at level 0.
    # data for this is in each corresponding ImageSection. 

    print("done!")
    input()
    